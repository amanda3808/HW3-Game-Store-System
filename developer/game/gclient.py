import socket
import threading
import tkinter as tk

HOST = '140.113.17.11'
PORT = 15455

class GuessClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        self.my_id = None
        self.game_over = False

        # ===== GUI =====
        self.root = tk.Tk()
        self.root.title("猜數字遊戲 Client")

        self.text = tk.Text(self.root, height=15, width=50, state=tk.DISABLED)
        self.text.pack(padx=10, pady=5)

        self.entry = tk.Entry(self.root)
        self.entry.pack(padx=10, pady=5)

        self.btn_guess = tk.Button(
            self.root,
            text="送出猜測",
            command=self.send_guess,
            state=tk.DISABLED
        )
        self.btn_guess.pack(pady=5)

        # ⭐ 離開按鈕一開始不顯示
        self.btn_exit = tk.Button(
            self.root,
            text="離開遊戲",
            command=self.exit_game
        )

        threading.Thread(target=self.receive, daemon=True).start()
        self.root.protocol("WM_DELETE_WINDOW", self.exit_game)
        self.root.mainloop()

    # ===== 工具 =====
    def log(self, msg):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, msg + "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    # ===== 送出猜測 =====
    def send_guess(self):
        guess = self.entry.get()
        if guess.isdigit():
            self.sock.sendall(f"GUESS:{guess}".encode())
            self.entry.delete(0, tk.END)
            self.btn_guess.config(state=tk.DISABLED)

    # ===== 接收資料 =====
    def receive(self):
        while True:
            try:
                data = self.sock.recv(1024).decode()
                if not data:
                    break

                for line in data.strip().split("\n"):
                    self.handle_message(line)
            except:
                break

    # ===== 處理 Server 訊息 =====
    def handle_message(self, line):
        if line.startswith("INFO"):
            self.log(line)
            if "你是玩家" in line:
                self.my_id = int(line[-1])

        elif line.startswith("TURN"):
            turn_id = int(line.split(":")[1])
            if turn_id == self.my_id and not self.game_over:
                self.log("👉 輪到你了")
                self.btn_guess.config(state=tk.NORMAL)
            else:
                self.btn_guess.config(state=tk.DISABLED)

        elif line.startswith("WIN"):
            self.game_over = True
            self.show_game_over(line)

        else:
            self.log(line)

    # ===== 遊戲結束畫面（無彈窗） =====
    def show_game_over(self, msg):
        self.log("========== 遊戲結束 ==========")
        self.log(msg)

        # 停用輸入
        self.btn_guess.config(state=tk.DISABLED)
        self.entry.config(state=tk.DISABLED)

        # ⭐ 顯示離開按鈕
        self.btn_exit.pack(pady=10)

    # ===== 離開遊戲 =====
    def exit_game(self):
        try:
            self.sock.close()
        except:
            pass
        self.root.destroy()

if __name__ == "__main__":
    GuessClient()
