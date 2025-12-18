from pathlib import Path
import sys, socket, threading
import tkinter as tk
from tkinter import filedialog

current = Path(__file__).resolve()
project_root = current.parent.parent
sys.path.append(str(project_root))
from common import send_msg, recv_msg, send_file, recv_file


SERVER_HOST = "140.113.17.11"   # Lobby Server IP
SERVER_PORT = 23729         # Lobby Server Port
folder_path = str(current.parent / "game")
conn = None

position = "Developer"
userid = None

def send_request(action, data=None):
    """發送 JSON 格式請求給伺服器"""
    msg = {"position": position, "action": action, "id": userid, "data": data or {}}
    send_msg(conn, msg)
    resp=recv_msg(conn)
    return resp


root = tk.Tk()
root.title("developer")
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
        userid = self.username.get()
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
        tk.Button(self.page, text="上架", command=self.newGame).grid(row=1, column=0)
        tk.Button(self.page, text="登出", command=self.logout).grid(row=1, column=1)
        tk.Label(self.page, text="MY GAME:").grid(row=3, column=0)

        r = send_request("QUERY_MYGAME", {})
        print(r)
        options = r.get("msg")
        self.var = tk.StringVar(value="") 
        for i, item in enumerate(options):
            tk.Radiobutton(self.page, text=item, value=item, variable=self.var).grid(row=4, column=i)
        tk.Button(self.page, text="更新", command=self.renew).grid(row=5, column=0)
        tk.Button(self.page, text="下架", command=self.delet).grid(row=5, column=1)
    
    def renew(self):
        item = self.var.get()
        print("更新:", item)
        self.page.destroy()
        renewPage(self.root,item)

    def delet(self):
        item = self.var.get()
        print("下架:", item)
        r = send_request("DELET", {"gname":item})
        print(r)
        self.page.destroy()
        mainPage(self.root)
    def newGame(self):
        self.page.destroy()
        newGamePage(self.root)


    def logout(self):
        r = send_request("LOGOUT", {})
        print(r)
        self.page.destroy()
        loginPage(self.root)

class newGamePage(object):
    def __init__(self, master=None):
        self.root = master
        self.page = tk.Frame(self.root)
        self.page.pack()

        tk.Label(self.page, text="遊戲名稱：").grid(row=0, column=0, pady=5)
        tk.Label(self.page, text="介紹：").grid(row=1, column=0, pady=5)

        self.gname = tk.Entry(self.page)
        self.intr = tk.Entry(self.page)

        self.gname.grid(row=0, column=1)
        self.intr.grid(row=1, column=1)

        tk.Button(self.page, text="server檔案", command=self.selServer).grid(row=2, column=0, pady=10)
        tk.Button(self.page, text="client檔案", command=self.selClient).grid(row=2, column=1, pady=10)

        tk.Button(self.page, text="上架", command=self.newGame).grid(row=4, column=0, pady=10)

    def selServer(self):
        self.sfile_path = filedialog.askopenfilename(initialdir=folder_path, title="請選擇要上傳的檔案")
        print("你選了：", self.sfile_path)
        if self.sfile_path:
            path = Path(self.sfile_path)
            self.sfile = path.name
            tk.Label(self.page, text= self.sfile).grid(row=3, column=0)
    def selClient(self):
        self.cfile_path = filedialog.askopenfilename(initialdir=folder_path, title="請選擇要上傳的檔案")
        print("你選了：", self.cfile_path)
        if self.cfile_path:
            path = Path(self.cfile_path)
            self.cfile = path.name
            tk.Label(self.page, text= self.cfile).grid(row=3, column=1)

    def newGame(self):
        if not self.sfile or not self.cfile:
            tk.Label(self.page, text= "先選擇檔案").grid(row=5, column=0)
        else:
            r = send_request("NEW_GAME", {"gname":self.gname.get(), "intr":self.intr.get(), "sfile":self.sfile, "cfile":self.cfile})
            print(r)
            if r.get("status") == "OK":
                msg = {"position": position, "action": "UPLOAD", "id": userid, "data": {}}
                send_msg(conn, msg)
                send_file(conn, folder_path, self.sfile)
                r=recv_msg(conn)
                print(r)
                msg = {"position": position, "action": "UPLOAD", "id": userid, "data": {}}
                send_msg(conn, msg)
                send_file(conn, folder_path, self.cfile)
                r=recv_msg(conn)
                print(r)
                self.page.destroy()
                mainPage(self.root)

class renewPage(object):
    def __init__(self, master=None,item=None):
        self.root = master
        self.item = item
        self.page = tk.Frame(self.root)
        self.page.pack()

        tk.Button(self.page, text="server檔案", command=self.selServer).grid(row=0, column=0, pady=10)
        tk.Button(self.page, text="client檔案", command=self.selClient).grid(row=0, column=1, pady=10)

        tk.Button(self.page, text="更新", command=self.renewGame).grid(row=2, column=0, pady=10)

    def selServer(self):
        self.sfile_path = filedialog.askopenfilename(initialdir=folder_path, title="請選擇要上傳的檔案")
        print("你選了：", self.sfile_path)
        if self.sfile_path:
            path = Path(self.sfile_path)
            self.sfile = path.name
            tk.Label(self.page, text= self.sfile).grid(row=1, column=0)
    def selClient(self):
        self.cfile_path = filedialog.askopenfilename(initialdir=folder_path, title="請選擇要上傳的檔案")
        print("你選了：", self.cfile_path)
        if self.cfile_path:
            path = Path(self.cfile_path)
            self.cfile = path.name
            tk.Label(self.page, text= self.cfile).grid(row=1, column=1)

    def renewGame(self):
        if not self.sfile or not self.cfile:
            tk.Label(self.page, text= "先選擇檔案").grid(row=3, column=0)
        else:
            r = send_request("RENEW", {"gname":self.item, "sfile":self.sfile, "cfile":self.cfile})
            print(r)
            if r.get("status") == "OK":
                msg = {"position": position, "action": "UPLOAD", "id": userid, "data": {}}
                send_msg(conn, msg)
                send_file(conn, folder_path, self.sfile)
                r=recv_msg(conn)
                print(r)
                msg = {"position": position, "action": "UPLOAD", "id": userid, "data": {}}
                send_msg(conn, msg)
                send_file(conn, folder_path, self.cfile)
                r=recv_msg(conn)
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
