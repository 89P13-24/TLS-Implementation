import ssl
import socket
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

def main():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE  # Skipping verification

    try:
        with socket.create_connection(('localhost', 8443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname='localhost') as ssock:
                logging.info("TLS Handshake with server complete.")
                logging.info(f"Server cipher: {ssock.cipher()}")
                logging.info(f"Server cert: {ssock.getpeercert()}")

                message = input("Enter message to send to server: ")
                ssock.sendall(message.encode())
                data = ssock.recv(1024).decode()
                logging.info(f"Received from server: {data}")
    except Exception as e:
        logging.error(f"Client encountered error: {e}")

if __name__ == "__main__":
    main()
