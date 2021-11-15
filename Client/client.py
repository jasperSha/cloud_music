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
FORMAT = "utf-8"
HEADER = 64
URL = "http://" + HOST + ":" + str(PORT)

my_data = b"Hello From here"


"""def send_message(server, message):
	msg = message.encode(FORMAT)
	msg_length = str(len(msg)).encode(FORMAT)
	#pad the message to the header length
	msg_length += b' ' * (64 - len(msg_length))
	server.send(msg_length)
	server.send(msg)"""

def send_get():
	r = requests.get(URL, stream=True)
	r.close()
	
def send_post():
	# file = {"file": open("README.md", "rb")}

	api = "/model/update"
	
	data = dict(songid = "flac1234")

	r = requests.post(URL + api, data=data, stream=True)
	print(r.content)	
	r.close()

def main():
	send_post()
	#send_get()
	


	"""with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect(ADDR)
		send_message(s, "POST")
		send_message(s, "file_name 9")"""


if __name__ == "__main__":
	main()
