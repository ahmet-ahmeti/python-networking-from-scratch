import socket
import select
import struct
import json

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("127.0.0.1", 5050))
server_socket.listen()

all_sockets = [server_socket]

def broadcast(message, sender_sock):
    for sock in all_sockets:
        if sock != sender_sock and sock != server_socket:
            sock.sendall(message)

def recvall(sock, n):
    buffer = b""
    while len(buffer) < n:
        chunk = sock.recv(n - len(buffer))
        if chunk == b"":
            raise ConnectionError("connection ended before data could be recived")
        buffer += chunk
    return buffer

try:
    while True:
        readable, _, _ = select.select(all_sockets, [], [], None)

        for sock in readable:
            if sock == server_socket:
                conn, addr = sock.accept()
                all_sockets.append(conn)
                print("new connection:", addr)
            else:
                try:
                    length_struct = recvall(sock, 4)
                    length = struct.unpack("!I", length_struct)[0]
                    length = min(length, 1024)

                    data = recvall(sock, length)
                    data = data.decode()
                    data = json.loads(data)

                    if data["type"] == "chat":
                        if data["text"] == "quit":

                            payload = {
                                "type" : "chat",
                                "user" : "Server",
                                "text" : f"{data['user']} has left the chat"
                            }
                            payload_bytes = json.dumps(payload).encode()
                            header = struct.pack("!I", len(payload_bytes))

                            broadcast(header + payload_bytes, sock)

                            all_sockets.remove(sock)
                            sock.close()
                        else:
                            payload_bytes = json.dumps(data).encode()
                            header = struct.pack("!I", len(payload_bytes))
                            broadcast(header + payload_bytes, sock)

                    if data["type"] == "join":
                        payload = {
                            "type" : "chat",
                            "user" : "Server",
                            "text" : f"{data['user']} has joined the chat"
                        }

                        payload_bytes = json.dumps(payload).encode()
                        header = struct.pack("!I", len(payload_bytes))

                        broadcast(header + payload_bytes, sock)
                    

                except (ConnectionError, KeyError):
                    print(f"failed to recive data from socket: {sock}")
                    all_sockets.remove(sock)
                    sock.close()

finally:
    server_socket.close()