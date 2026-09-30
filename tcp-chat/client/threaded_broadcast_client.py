import socket
import threading
import struct
import json
 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 5050))
 
def recvall(sock, n):
    buffer = b""
    while len(buffer) < n:
        chunk = sock.recv(n - len(buffer))
        if chunk == b"":
            raise ConnectionError("connection ended before data could be recived")
        buffer += chunk
    return buffer
 
def recive_loop(sock):
    while True:
        length_struct = recvall(sock, 4)
        length = struct.unpack("!I", length_struct)[0]
        
        data = recvall(sock, length)
        data = data.decode()
        data = json.loads(data)
 
        print(f"{data['user']}: {data['text']}")
 
thread = threading.Thread(target=recive_loop, args=(client_socket, ))
thread.start()
 
username = input("Enter username: ")

payload = {
    "type" : "join",
    "user" : username
}

payload_bytes = json.dumps(payload).encode()
header = struct.pack("!I", len(payload_bytes))

client_socket.sendall(header + payload_bytes)
 
while True:
    message = input("Enter message: ")
    payload = {
        "type" : "chat",
        "user" : username,
        "text" : message
    }
    payload_bytes = json.dumps(payload).encode()

    header = struct.pack("!I", len(payload_bytes))
    client_socket.sendall(header + payload_bytes)

    if payload["text"] == "quit":
        break
 
client_socket.close()
