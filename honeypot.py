


import socket
import threading
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename='honeypot.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 2222       # Custom SSH-like port

def handle_client(client_socket, addr):
    try:
        client_socket.sendall(b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.3\n")
        data = client_socket.recv(1024).decode('utf-8', errors='ignore')
        
        # Fake login
        client_socket.sendall(b"login as: ")
        username = client_socket.recv(1024).decode('utf-8', errors='ignore').strip()

        client_socket.sendall(b"{0}@hostname's password: ".format(username).encode())
        password = client_socket.recv(1024).decode('utf-8', errors='ignore').strip()

        log_msg = f"[LOGIN ATTEMPT] IP: {addr[0]} | Port: {addr[1]} | Username: {username} | Password: {password}"
        logging.info(log_msg)

        # Fake response
        client_socket.sendall(b"Permission denied, please try again.\n")
    except Exception as e:
        logging.error(f"Error handling client {addr}: {e}")
    finally:
        client_socket.close()
def start_honeypot():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(100)
    print(f"[+] Honeypot listening on port {PORT}...")

    try:
        while True:
            client, addr = server.accept()
            print(f"[!] Connection from {addr}")
            thread = threading.Thread(target=handle_client, args=(client, addr))
            thread.start()
    except KeyboardInterrupt:
        print("\n[!] Honeypot shutting down.")
        server.close()

if __name__ == "__main__":
    start_honeypot()


