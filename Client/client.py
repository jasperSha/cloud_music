"""
Client program to test along side with server
"""
import socket
import requests
import os

# Constants
PORT =  9002
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)
MAX_BUFFER = 1024
FORMAT = "utf-8"

def initialize_user():
	message = "GET /user/initialize HTTP/1.1\r\n"
	msg = message.encode(FORMAT)

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect(ADDR)
			send_message(s, msg)

def update_model():

	message = """POST /model/update HTTP/1.1\r
Content-Length: 15\r\n\r
sondid=flac1234"""
	msg = message.encode(FORMAT)

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect(ADDR)
			send_message(s, msg)

def get_playlist():
	message = "GET /playlist HTTP/1.1\r\n"
	msg = message.encode(FORMAT)

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect(ADDR)
			send_message(s, msg)


def send_message(server, msg):
	# send the message to the server
	server.send(msg)
	response  = server.recv(MAX_BUFFER).decode(FORMAT)
	print(response)

def main():

	user_input = input("""What would you like to do?
[1] Initialize a new user?
[2] Update the Server model?
[3] Get a playlist from the server?
[4] Quit\n""")

	while user_input != "4":
		if user_input == "1":
			initialize_user()
		elif user_input == "2":
			update_model()
		else:
			get_playlist()
		

		user_input = input("""What would you like to do?
[1] Initialize a new user?
[2] Update the Server model?
[3] Get a playlist from the server?
[4] Quit\n""")
		os.system("clear")


if __name__ == "__main__":
	main()
