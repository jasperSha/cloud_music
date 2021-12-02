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
			response = send_message(s, msg)
			if response is not None:
				# do something to initiaze the user
				return
			else:
				return -1

def update_model():

	message = """POST /model/update HTTP/1.1\r
Content-Length: 15\r\n\r
sondid=flac1234"""
	msg = message.encode(FORMAT)

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect(ADDR)
			response = send_message(s, msg)
			if response is not None:
				# everything is ok to exit
				return
			else:
				# there was an error updating the model
				return -1

def get_playlist():
	message = "GET /playlist HTTP/1.1\r\n"
	msg = message.encode(FORMAT)

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect(ADDR)
			response = send_message(s, msg)
			if response is not None:
				# do something with the playlist received
				return
			else:
				# there was an error updating the model
				return -1
			

def handle_error(error):
	print(f"Received {error.split()[1:]} from the server")

def handle_response(r):
	#split the response into managable pieces
	response_parsed = r.split("\r\n\r\n")
	if len(response_parsed) > 1:
		# we know this will be ok because there is a content length
		response_header = response_parsed[0]
		response_content = response_parsed[1]
	else:
		if int(response_parsed.split()[1]) >= 400:
			handle_error(response_parsed)
			return None
		else:
			return "ok"

def send_message(server, msg):
	# send the message to the server
	server.send(msg)
	response  = server.recv(MAX_BUFFER).decode(FORMAT)
	# handle server response
	return handle_response(response)

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
