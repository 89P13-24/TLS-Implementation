import ssl
import socket
import threading
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

def handle_client(conn, addr):
    try:
        logging.info(f"TLS Handshake done with client {addr}")
        logging.info(f"Client cipher: {conn.cipher()}")
        logging.info(f"Client cert: {conn.getpeercert()}")

        data = conn.recv(1024).decode()
        logging.info(f"Received from client {addr}: {data}")

        conn.sendall(b"Hello from TLS Server!")
    except Exception as e:
        logging.error(f"Error with client {addr}: {e}")
    finally:
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
        logging.info(f"Connection with {addr} closed.")

def main():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    bindsocket = socket.socket()
    bindsocket.bind(('localhost', 8443))
    bindsocket.listen(5)
    logging.info("Server listening on port 8443...")

    try:
        while True:
            newsocket, fromaddr = bindsocket.accept()
            conn = context.wrap_socket(newsocket, server_side=True)
            threading.Thread(target=handle_client, args=(conn, fromaddr)).start()
    except KeyboardInterrupt:
        logging.info("Server shutting down...")
    finally:
        bindsocket.close()

if __name__ == "__main__":
    main()
