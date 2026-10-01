import socket
import struct
import threading
import json
 
try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 
    server_socket.bind(("127.0.0.1", 5050))
    server_socket.listen()
 
    lock = threading.Lock()
 
    client_sockets = []
 
    def recvall(sock, n):
        buffer = b""
        while len(buffer) < n:
            chunk = sock.recv(n - len(buffer))
            if chunk == b"":
                raise ConnectionError("connection ended before data was recived")
            buffer += chunk
        return buffer
 
    def broadcast(message, sender_sock):
        with lock:
            for sock in client_sockets:
                if sock != sender_sock:
                    sock.sendall(message)
 
    def handle_client(sock):
        try:
            with lock:
                client_sockets.append(sock)
 
            while True:
                length_struct = recvall(sock, 4)
                length = struct.unpack("!I", length_struct)[0]

                data = recvall(sock, length)
                data = data.decode()
                data = json.loads(data)

                if data["type"] == "join":
                    payload = {
                        "type" : "chat",
                        "user" : "Server",
                        "text" : f"{data["user"]} has joined the chat"
                    }
                    payload_bytes = json.dumps(payload).encode()
                    header = struct.pack("!I", len(payload_bytes))

                    broadcast(header + payload_bytes, sock)

                elif data["type"] == "chat":

                    if data["text"] == "quit":
                        payload = {
                            "type" : "chat",
                            "user" : "Server",
                            "text" : f"{data["user"]} has left the chat"
                        }
                        payload_bytes = json.dumps(payload).encode()
                        header = struct.pack("!I", len(payload_bytes))

                        broadcast(header + payload_bytes, sock)
                        return
                    else:
                        payload_bytes = json.dumps(data).encode()
                        header = struct.pack("!I", len(payload_bytes))

                        broadcast(header + payload_bytes, sock)

        finally:
            with lock:
                client_sockets.remove(sock)
            sock.close()
 
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, ))
        thread.start()
 
finally:
    server_socket.close()
