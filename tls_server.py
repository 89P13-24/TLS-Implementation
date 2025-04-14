# tls_server.py
import ssl
import socket

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

bindsocket = socket.socket()
bindsocket.bind(('localhost', 8443))
bindsocket.listen(5)
print("Server listening on port 8443...")

while True:
    newsocket, fromaddr = bindsocket.accept()
    with context.wrap_socket(newsocket, server_side=True) as conn:
        print("TLS Handshake done with client.")
        print("Client cipher:", conn.cipher())
        msg = conn.recv(1024).decode()
        print("Received from client:", msg)
        conn.sendall(b"Hello from TLS Server!")
