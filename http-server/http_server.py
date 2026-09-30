import socket
import select

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_sock.bind(("127.0.0.1", 5050))
server_sock.listen()

all_socks = [server_sock]

def recv_http_header(sock):
    buffer = b""
    while b"\r\n\r\n" not in buffer:
        chunk = sock.recv(1024)
        if chunk == b"":
            raise ConnectionError("connectipn was closed before data could be recived")
        buffer += chunk
    return buffer

try:
    while True:
        readable, _, _ = select.select(all_socks, [], [], None)

        for sock in readable:
            if sock == server_sock:
                conn, addr = sock.accept()
                all_socks.append(conn)

            else:
                try:
                    data = recv_http_header(sock)
                    line, sep, data = data.partition(b"\r\n")
                    method, path, version = line.split(b" ")

                    allowed_paths = {
                        "/" : "index.html",
                        "/style.css" : "style.css"
                    }

                    path_str = path.decode()

                    if path_str in allowed_paths:
                        filename = allowed_paths[path_str]

                        with open(filename) as f:
                            body = f.read()

                        status_line = f"{version.decode()} 200 OK"
                    else:
                        status_line = f"{version.decode()} 404 Not Found"
                        body = "<h1>404 Not Found</h1>"

                    body_bytes = body.encode()

                    response = f"{status_line}\r\nContent-Type: text/html\r\nContent-Length: {len(body_bytes)}\r\n\r\n"
                    response_bytes = response.encode()

                    sock.sendall(response_bytes + body_bytes)
                    all_socks.remove(sock)
                    sock.close()
                except ConnectionError:
                    all_socks.remove(sock)
                    sock.close()
                    pass
finally:
    server_sock.close()