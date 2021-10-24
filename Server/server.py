"""
Python server for clients to accees and upload their model.
"""

# import
import socket
import threading

# Constants
MAX_BUFFER = 1024
PORT = 9001
FORMAT = "utf-8"
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)


# POST

# handle client requests
def handle_client(conn, addr):
	with conn:
		print(f"[New connection...{addr}]")
		connected = True
		while connected:
			data = conn.recv(MAX_BUFFER).decode(FORMAT)
			if not data:
				connected = False
			else:
				print("[Message recv]   ", data)
	print("[Closed connection]")

def main():
	print(HOST)
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
		server.bind(ADDR)
		server.listen()
		while True:
			conn, addr = server.accept()
			handle_client(conn, addr)

if __name__ == "__main__":
	main()
