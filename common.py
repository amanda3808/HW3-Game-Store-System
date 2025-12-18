import struct, json, os

MAX_LEN = 65536

def send_msg(conn, obj):
    body = json.dumps(obj).encode("utf-8")
    length = struct.pack("!I", len(body))
    conn.sendall(length + body)

def recv_msg(conn):
    header = b""
    while len(header) < 4:
        packet = conn.recv(4 - len(header))
        if not packet:
            return None
        header += packet
    (length,) = struct.unpack("!I", header)
    if length <= 0 or length > MAX_LEN:
        return None
    body = b""
    while len(body) < length:
        packet = conn.recv(length - len(body))
        if not packet:
            return None
        body += packet
    return json.loads(body.decode("utf-8"))


def send_file(conn, folder_path, filename):
    print("開始send_file")
    file_path = os.path.join(folder_path, filename)
    filesize = os.path.getsize(file_path)

    filename_bytes = filename.encode("utf-8")

    # 1️⃣ 傳 filename 長度（4 bytes）
    conn.sendall(struct.pack("!I", len(filename_bytes)))

    # 2️⃣ 傳 filename
    conn.sendall(filename_bytes)

    # 3️⃣ 傳 filesize（8 bytes）
    conn.sendall(struct.pack("!Q", filesize))


    with open(file_path, "rb") as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            conn.sendall(data)

    print("上傳完成")

def recv_all(conn, size):
    data = b""
    while len(data) < size:
        packet = conn.recv(size - len(data))
        if not packet:
            raise ConnectionError("連線中斷")
        data += packet
    return data

def recv_file(conn, folder_path):
    # 1️⃣ 收 filename 長度
    raw = recv_all(conn, 4)
    filename_len = struct.unpack("!I", raw)[0]

    # 2️⃣ 收 filename
    filename = recv_all(conn, filename_len).decode("utf-8")
    print("要下載的檔案：", filename)

    # 3️⃣ 收 filesize
    raw = recv_all(conn, 8)
    filesize = struct.unpack("!Q", raw)[0]



    file_path = os.path.join(folder_path, filename)
    with open(file_path, "wb") as f:
        total = 0
        while total < filesize:
            data = conn.recv(min(1024, filesize - total))
            if not data:
                break
            f.write(data)
            total += len(data)

    print("下載完成！")
    return filename