import socket
import struct
import threading
 
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
 
                if data == b"quit":
                    break
 
                broadcast(length_struct + data, sock)
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
