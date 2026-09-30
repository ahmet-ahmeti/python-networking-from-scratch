import socket
import threading
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_addr = ("127.0.0.1", 5050)

def handle_recive():
    while True:
        data = sock.recvfrom(1024)[0].decode()

        data = json.loads(data)

        if data["type"] == "join":
            print(f"{data["user"]} has joined the chat")

        elif data["type"] == "chat":
            print(f"{data["user"]}: {data["text"]}")

thread = threading.Thread(target=handle_recive, args=(), daemon=True)
thread.start()

username = input("Enter username: ")

payload = {
    "type" : "join",
    "user" : username
}

payload_bytes = json.dumps(payload).encode()

sock.sendto(payload_bytes, server_addr)

while True:
    message = input("Enter message: ")

    payload = {
        "type" : "chat",
        "user" : username,
        "text" : message
    }

    payload_bytes = json.dumps(payload).encode()

    if message == "quit":
        break

    sock.sendto(payload_bytes, server_addr)