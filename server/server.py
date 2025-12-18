from pathlib import Path
import sys, socket, threading
from db import create, read, save, query, remove
import subprocess
import os

# main.py 路徑
current = Path(__file__).resolve()

# 專案根目錄
project_root = current.parent.parent
sys.path.append(str(project_root))

from common import send_msg, recv_msg, send_file, recv_file

HOST = '0.0.0.0'
PORT = 23729
folder_path = str(current.parent / "game")

def handle_client(conn, addr):
    print(f"[Lobby] Connected: {addr}")
    try:
        while True:
            msg = recv_msg(conn)
            if msg is None:
                break
            print(f"[SERVER] Received: {msg}")
            position = msg.get("position")
            action = msg.get("action")
            userid = msg.get("id")
            data = msg.get("data")
            response = {"status": "ERR", "msg": "Unknown error"}
            p = None

            if position == "Developer":
                if action == "REGISTER":  #"data":{"pwd":"..."}
                    pwd = data.get("pwd")
                    if not userid or not pwd:
                        response = {"status":"ERR","msg":"missing fields"}
                    else:
                        add = {"pwd": pwd, "online":0}
                        response = create(position, userid, add)      
                # LOGIN
                elif action == "LOGIN":  #"data":{"pwd":"..."}
                    pwd = data.get("pwd")
                    if not userid or not pwd:
                        response = {"status":"ERR","msg":"missing fields"}
                    else:
                        r = read(position, userid)
                        if r.get("status") == "ERR":
                            response = r
                        else:
                            user = r.get("msg")
                            if user["pwd"] != pwd:
                                response = {"status":"ERR","msg":"Wrong password"}
                            elif user["online"] == 1:
                                response = {"status":"ERR","msg":"User is using"}
                            else:
                                user["online"] = 1
                                r = save(position, userid, user)
                                if r.get("status") == "OK":
                                    response = {"status":"OK","msg":"LOGIN_SUCCESS"}
                                    print(f"[SERVER] {userid} logged in.")
                # LOGOUT
                elif action == "LOGOUT":  #"data":{}
                    r = read(position, userid)
                    if r.get("status") == "OK":
                        user = r.get("msg")
                        user["online"] = 0
                        save(position, userid, user)
                        response = {"status":"OK","msg":"LOGOUT_SUCCESS"}
                        print(f"[SERVER] {userid} logged out.")
                # QUERY_MYGAME
                elif action == "QUERY_MYGAME":  #"data":{}
                    r = query("Game", "owner", userid)
                    response = r
                # NEW_GAME
                elif action == "NEW_GAME":  #"data":{"gname":"...", "intr":"...", "sfile":"...", "cfile":"..."}
                    gname = data.get("gname")
                    sfile = data.get("sfile")
                    cfile = data.get("cfile")
                    sfile_path = Path(folder_path)/sfile
                    cfile_path = Path(folder_path)/cfile
                    if sfile_path.exists() or cfile_path.exists():
                        response = {"status":"ERR","msg":"File exists."}
                    else:
                        add = {"valid": 1, "owner":userid, "intr":data.get("intr"), "sfile":sfile, "cfile":cfile, "comment":[]}
                        response = create("Game", gname, add)  
                # UPLOAD
                elif action == "UPLOAD":
                    recv_file(conn, folder_path)
                    response = {"status":"OK","msg":"upload."}
                # DELET
                elif action == "DELET":
                    gname = data.get("gname")
                    r = read("Game", gname)
                    if r.get("status") == "OK":
                        game = r.get("msg")
                        game["valid"] = 0
                        save("Game", gname, game)
                        response = {"status":"OK","msg":"delet."}
                # RENEW
                elif action == "RENEW": #"data":{"gname":"...", "sfile":"...", "cfile":"..."}
                    gname = data.get("gname")
                    sfile = data.get("sfile")
                    cfile = data.get("cfile")
                    sfile_path = Path(folder_path)/sfile
                    cfile_path = Path(folder_path)/cfile
                    if sfile_path.exists() or cfile_path.exists():
                        response = {"status":"ERR","msg":"File exists."}
                    else:
                        r = read("Game", gname)
                        if r.get("status") == "OK":
                            game = r.get("msg")
                            game["sfile"] = sfile
                            game["cfile"] = cfile
                            save("Game", gname, game)
                        response = {"status":"OK","msg":"wait upload."}
            elif position == "User":
                if action == "REGISTER":  #"data":{"pwd":"..."}
                    pwd = data.get("pwd")
                    if not userid or not pwd:
                        response = {"status":"ERR","msg":"missing fields"}
                    else:
                        add = {"pwd": pwd, "online":0}
                        response = create(position, userid, add)      
                # LOGIN
                elif action == "LOGIN":  #"data":{"pwd":"..."}
                    pwd = data.get("pwd")
                    if not userid or not pwd:
                        response = {"status":"ERR","msg":"missing fields"}
                    else:
                        r = read(position, userid)
                        if r.get("status") == "ERR":
                            response = r
                        else:
                            user = r.get("msg")
                            if user["pwd"] != pwd:
                                response = {"status":"ERR","msg":"Wrong password"}
                            elif user["online"] == 1:
                                response = {"status":"ERR","msg":"User is using"}
                            else:
                                user["online"] = 1
                                r = save(position, userid, user)
                                if r.get("status") == "OK":
                                    response = {"status":"OK","msg":"LOGIN_SUCCESS"}
                                    print(f"[SERVER] {userid} logged in.")
                # LOGOUT
                elif action == "LOGOUT":  #"data":{}
                    r = read(position, userid)
                    if r.get("status") == "OK":
                        user = r.get("msg")
                        user["online"] = 0
                        save(position, userid, user)
                        response = {"status":"OK","msg":"LOGOUT_SUCCESS"}
                        print(f"[SERVER] {userid} logged out.")
                # QUERY_MYGAME
                elif action == "QUERY_MYGAME":  #"data":{}
                    r = query("Game", "valid", 1)
                    response = r
                # SELECT_GAME
                elif action == "SELECT_GAME":  #"data":{"gname":"..."}
                    gname = data.get("gname")
                    r = read("Game", gname)
                    response = r
                # DOWNLOAD
                elif action == "DOWNLOAD": #"data":{"gname":"..."}
                    gname = data.get("gname")
                    r = read("Game", gname)
                    info = r.get("msg")
                    cfile = info.get("cfile")
                    send_file(conn, folder_path, cfile)
                    response = {"status":"OK","msg":"download."}
                # QUERY_ROOM
                elif action == "QUERY_ROOM":  #"data":{"gname":"..."}
                    gname = data.get("gname")
                    r = query("Room", "gname", gname)
                    response = r
                # CREATE_ROOM
                elif action == "CREATE_ROOM":  #"data":{"gname":"..."}
                    gname = data.get("gname")
                    add = {"gname": gname}
                    r = read("Game", gname)
                    info = r.get("msg")
                    sfile = info.get("sfile")
                    r = create("Room", userid, add) 
                    if r.get("status") == "OK":
                        p=subprocess.Popen([sys.executable, os.path.join(folder_path, sfile)])
                    response = r
                # CLOSE_ROOM
                elif action == "CLOSE_ROOM":  #"data":{}
                    r = remove("Room", userid)
                    if p is not None and p.poll() is None:
                        p.kill()
                    if r.get("status") == "OK":
                        response = {"status":"OK","msg":"CLOSE_ROOM_SUCCESS"}
                        print(f"[SERVER] {userid} closed the room.")
                    else:
                        response = {"status":"ERR","msg":r.get("msg")}
                # COMMENT
                elif action == "COMMENT":  #"data":{"gname":"...", "comm":"..."}
                    gname = data.get("gname")
                    comm = data.get("comm")
                    r = read("Game", gname)
                    if r.get("status") == "OK":
                        info = r.get("msg")
                        info["comment"].append(comm)
                        save("Game", gname, info)
                        response = {"status":"OK","msg":"comment."}

            else :
                response = {"status":"ERR","msg":"Unknow action."}
            send_msg(conn, response)
    except Exception as e:
        print("[Lobby ERROR]", e)
    finally:
        conn.close()
        r = read(position, userid)
        if r.get("status") == "OK":
            user = r.get("msg")
            user["online"] = 0
            save(position, userid, user)
        remove("Room", userid)
        if p is not None and p.poll() is None:
            p.kill()
        print(f"[Lobby] Disconnected: {addr}")






def run_lobby():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    print(f"[Lobby] Listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    run_lobby()