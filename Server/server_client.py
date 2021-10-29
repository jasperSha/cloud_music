"""
Client program to test along side with server
"""
import socket

PORT =  9001
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)


def main():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect(ADDR)
		s.sendall(b"Hello World!")


if __name__ == "__main__":
	main()
