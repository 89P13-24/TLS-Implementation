# tls_client.py
import ssl
import socket

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE  # Skip verification for self-signed cert

with socket.create_connection(('localhost', 8443)) as sock:
    with context.wrap_socket(sock, server_hostname='localhost') as ssock:
        print("TLS Handshake with server complete.")
        print("Server cipher:", ssock.cipher())
        ssock.sendall(b"Hello from TLS Client!")
        data = ssock.recv(1024).decode()
        print("Received from server:", data)
