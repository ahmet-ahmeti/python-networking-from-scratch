# Socket Programming From Scratch

Small networking projects built using Python's built-in `socket` module, without frameworks. Mainly made to get a better understanding of how TCP, UDP, framing, and concurrency work.

## tcp-chat/

Multi-client TCP chat using length-prefixed JSON messages: `[4-byte length][JSON payload]`.

* `threaded/server.py` one thread per client, shared client list + lock.
* `select-based/server.py` single thread using `select()` for all sockets.
* `client.py` two threads: one for `input()`, one for receiving messages.

Run the server, then open `client.py` in a few terminals.

## udp-chat/

Same basic idea, but with UDP. No connections or framing since each message is a datagram.

The server keeps track of known clients and removes ones that haven't sent anything for 10s. It also validates incoming JSON before broadcasting it.

Run `server.py`, then `client.py` in a few terminals.

## http-server/

A small single-threaded HTTP server using `select()`.

It parses the request line, routes requests using an allowlist, and serves files with the correct `Content-Length`. Path traversal is blocked since requested paths are matched against the allowlist instead of being passed directly to `open()`.

Run `server.py` and open `http://127.0.0.1:5050/` or use `curl -i`.
