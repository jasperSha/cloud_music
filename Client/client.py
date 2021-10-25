"""
Client program to test along side with server
"""
import socket

# Constants
PORT =  9002
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)
FORMAT = "utf-8"
HEADER = 64


def send_message(server, message):
	msg = message.encode(FORMAT)
	msg_length = str(len(msg)).encode(FORMAT)
	#pad the message to the header length
	msg_length += b' ' * (64 - len(msg_length))
	server.send(msg_length)
	server.send(msg)

def main():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect(ADDR)
		send_message(s, "POST")
		send_message(s, "file_name 9")


if __name__ == "__main__":
	main()
