import socket
import threading
import random
import time

HOST = '0.0.0.0'
PORT = 15455
MAX_CLIENTS = 3

clients = []
current_turn = 0
answer = random.randint(1, 100)
game_over = False

print("答案是（Server端可見）：", answer)

def broadcast(msg):
    for c in clients:
        c.sendall(msg.encode())

def handle_client(conn, cid):
    global current_turn, game_over

    conn.sendall(f"INFO:你是玩家 {cid}\n".encode())

    while not game_over:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            if data.startswith("GUESS"):
                if current_turn != cid - 1:
                    conn.sendall("INFO:還沒輪到你\n".encode())
                    continue

                guess = int(data.split(":")[1])

                if guess < answer:
                    broadcast(f"INFO:玩家 {cid} 猜 {guess} → 太小\n")
                elif guess > answer:
                    broadcast(f"INFO:玩家 {cid} 猜 {guess} → 太大\n")
                else:
                    broadcast(f"WIN:玩家 {cid} 猜中了！答案是 {answer}\n")
                    game_over = True
                    break

                current_turn = (current_turn + 1) % MAX_CLIENTS
                broadcast(f"TURN:{current_turn + 1}\n")

        except:
            break

    conn.close()

def main():
    global current_turn

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    print("Server 啟動，等待 3 位玩家...")

    while len(clients) < MAX_CLIENTS:
        conn, addr = s.accept()
        clients.append(conn)
        cid = len(clients)
        threading.Thread(
            target=handle_client,
            args=(conn, cid),
            daemon=True
        ).start()
        print(f"玩家 {cid} 已連線")

    broadcast("INFO:遊戲開始！\n")
    broadcast("TURN:1\n")

    while not game_over:
        time.sleep(1)

    print("遊戲結束，Server 關閉")
    s.close()

if __name__ == "__main__":
    main()
