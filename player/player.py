from pathlib import Path
import sys, socket, threading
import tkinter as tk
from tkinter import filedialog
import subprocess
import os

current = Path(__file__).resolve()
project_root = current.parent.parent
sys.path.append(str(project_root))
from common import send_msg, recv_msg, send_file, recv_file


SERVER_HOST = "140.113.17.11"   # Lobby Server IP
SERVER_PORT = 23729         # Lobby Server Port
folder_path = str(current.parent / "game")
conn = None

position = "User"
userid = None

def send_request(action, data=None):
    """發送 JSON 格式請求給伺服器"""
    msg = {"position": position, "action": action, "id": userid, "data": data or {}}
    send_msg(conn, msg)
    resp=recv_msg(conn)
    return resp


root = tk.Tk()
root.title("player")
root.geometry("400x200")


class loginPage(object):
    def __init__(self, master=None):
        self.root = master
        self.page = tk.Frame(self.root)
        self.page.pack()

        tk.Label(self.page, text="帳號：").grid(row=0, column=0, pady=5)
        tk.Label(self.page, text="密碼：").grid(row=1, column=0, pady=5)

        self.username = tk.Entry(self.page)
        self.password = tk.Entry(self.page, show="*")

        self.username.grid(row=0, column=1)
        self.password.grid(row=1, column=1)

        tk.Button(self.page, text="登入", command=self.login).grid(row=2, column=0, pady=10)
        tk.Button(self.page, text="註冊", command=self.register).grid(row=2, column=1, pady=10)

    def login(self):
        global userid
        global folder_path
        userid = self.username.get()
        folder_path = str(current.parent / "game"/ userid)
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        pwd = self.password.get()
        r = send_request("LOGIN", {"pwd": pwd})
        print(r)

        if r.get("status") == "OK":
            self.page.destroy()
            mainPage(self.root)

    def register(self):
        global userid
        userid = self.username.get()
        pwd = self.password.get()
        r = send_request("REGISTER", {"pwd": pwd})
        print(r)
        if r.get("status") == "OK":
            tk.Label(self.page, text= userid+"已註冊").grid(row=3, column=0)

class mainPage(object):
    def __init__(self, master=None):
        self.root = master
        self.page = tk.Frame(self.root)
        self.page.pack()

        tk.Label(self.page, text=userid+"已登入").grid(row=0, column=0, pady=20)
        tk.Button(self.page, text="登出", command=self.logout).grid(row=0, column=1)
        tk.Label(self.page, text="可以玩的遊戲:").grid(row=3, column=0)

        r = send_request("QUERY_MYGAME", {})
        print(r)
        options = r.get("msg")
        self.var = tk.StringVar(value="") 
        if not options:
            tk.Label(self.page, text="沒有遊戲").grid(row=4, column=0)
        else:
            for i, item in enumerate(options):
                tk.Radiobutton(self.page, text=item, value=item, variable=self.var).grid(row=4, column=i)
            tk.Button(self.page, text="選擇", command=self.select).grid(row=5, column=0)

    
    def select(self):
        item = self.var.get()
        self.page.destroy()
        gamePage(self.root,item)

    def logout(self):
        r = send_request("LOGOUT", {})
        print(r)
        self.page.destroy()
        loginPage(self.root)

class gamePage(object):
    def __init__(self, master=None,item=None):
        self.root = master
        self.item = item
        self.page = tk.Frame(self.root)
        self.page.pack()

        r = send_request("SELECT_GAME", {"gname":self.item})
        print(r)
        info = r.get("msg")
        if info["valid"] == 0:
            self.page.destroy()
            mainPage(self.root)

        tk.Label(self.page, text=self.item).grid(row=0, column=0, pady=20)
        tk.Label(self.page, text="介紹:" + info["intr"]).grid(row=1, column=0)
        self.cfile = info.get("cfile")
        cfile_path = Path(folder_path)/self.cfile
        comments = info.get("comment")
        if not cfile_path.exists():
            tk.Button(self.page, text="下載/更新", command=self.download).grid(row=2, column=0, pady=10)
        else:
            tk.Button(self.page, text="開始遊玩", command=self.startGame).grid(row=2, column=0, pady=10)
        if comments:
            tk.Label(self.page, text="評論:").grid(row=3, column=0)
            for i, item in enumerate(comments):
                tk.Label(self.page, text=item).grid(row=4+i, column=0)


    def download(self):
        msg = {"position": position, "action": "DOWNLOAD", "id": userid, "data": {"gname":self.item}}
        send_msg(conn, msg)
        recv_file(conn, folder_path)
        r=recv_msg(conn)
        print(r)

        self.page.destroy()
        gamePage(self.root,self.item)
    
    def startGame(self):
        self.page.destroy()
        roomPage(self.root,self.item,self.cfile)

class roomPage(object):
    def __init__(self, master=None,item=None,cfile=None):
        self.root = master
        self.item = item
        self.cfile = cfile
        self.page = tk.Frame(self.root)
        self.page.pack()
        tk.Label(self.page, text=self.item).grid(row=0, column=0, pady=20)
        tk.Button(self.page, text="建立新房間", command=self.createRoom).grid(row=1, column=0)
        tk.Label(self.page, text="可以加入的房間:").grid(row=2, column=0)

        r = send_request("QUERY_ROOM", {"gname":self.item})
        print(r)
        options = r.get("msg")
        self.var = tk.StringVar(value="") 
        if not options:
            tk.Label(self.page, text="沒有房間").grid(row=4, column=0)
        else:
            for i, item in enumerate(options):
                tk.Radiobutton(self.page, text=item, value=item, variable=self.var).grid(row=4, column=i)
            tk.Button(self.page, text="加入", command=self.join).grid(row=5, column=0)

    
    def createRoom(self):
        r = send_request("CREATE_ROOM", {"gname":self.item})
        print(r)
        self.page.destroy()
        roomPage(self.root,self.item,self.cfile)


    def join(self):
        i = self.var.get()
        self.root.withdraw()
        subprocess.run([sys.executable, os.path.join(folder_path, self.cfile)])
        self.root.deiconify()
        if i == userid:
            r = send_request("CLOSE_ROOM", {})
            print(r)
        self.page.destroy()
        commentPage(self.root,self.item)

class commentPage(object):
    def __init__(self, master=None,item=None):
        self.root = master
        self.item = item
        self.page = tk.Frame(self.root)
        self.page.pack()

        tk.Label(self.page, text="評論：").grid(row=0, column=0, pady=5)

        self.comment = tk.Entry(self.page)
        self.comment.grid(row=0, column=1)

        tk.Button(self.page, text="回主頁", command=self.home).grid(row=2, column=0, pady=10)

    def home(self):
        comm = self.comment.get()
        if comm:
            r = send_request("COMMENT", {"gname":self.item, "comm": comm})
            print(r)

        self.page.destroy()
        mainPage(self.root)





def main():
    print(f"連線中 {SERVER_HOST}:{SERVER_PORT} ...")
    try:
        global conn
        conn = socket.create_connection((SERVER_HOST, SERVER_PORT))
    except Exception as e:
        print("無法連線伺服器:", e)
        return
    print("已連線到 Lobby Server\n")
    loginPage(root)
    root.mainloop()


if __name__ == "__main__":
    main()
# 啟動
