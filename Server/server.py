"""
Python server for clients to accees and upload their model.
"""

# imports
import socket
import threading

# Constants
MAX_BUFFER = 1024
PORT = 9002
FORMAT = "utf-8"
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)

VALID_CALLS = {"/model/update": "POST", "/user/initialize": "GET", "/playlist": "GET"}

class HTTP_Parser:
	
	def __init__(self, client_request, conn):
		self.request = client_request
		self.sockect = conn
		self.error = None
		


	def HTTP_information(self):
		request_line = self.lines[0].split()
		self.method = request_line[0]
		self.api_path = request_line[1]
		self.protocol = request_line[2]
	
	def contents(self):
		# determine if there is more information to read
		self.content = self.lines[-1]
		if len(self.request) == MAX_BUFFER and len(self.content) < self.file_size:
			# we have not gotten the full message read more
			while len(client_request) == MAX_BUFFER and len(self.content) < self.file_size:
				# read more information from the client in order to construct
				client_request = self.socket.recv(MAX_BUFFER).decode(FORMAT)
				self.content += client_request
		if len(self.content) != self.file_size:
			# we have not received all of the desired information
			self.error = 406

	def check_error(self):
		if self.error != None:
			 # make  instance of error class
			 return True # to exit
		else:
			return False

	
	def check_API(self):
		if self.api_path not in VALID_CALLS:
			self.error = 404
		if self.method != VALID_CALLS[self.api_path]:
			self.error = 405
		
	
	def check_protocol(self):
		if self.protocol != "HTTP/1.1":
			self.error = 400

	def POST_request(self):
		# get content length
		if "Content-Length" in self.lines[6]:
			# get integer size coresponding to file length from requesrt
			self.file_size = int(self.lines[6].split()[1])
		else:
			self.error  = 400
			return
		self.contents()

	def GET_request(self):
		if self.api_path == "/user/initialize":
			# go get tree for client
			pass
		else:
			song_id = self.lines[-1]
			# create playlist for the client


	def parse_request(self):
		"""
		Break down the user request by seperating into new lines
		"""
		self.lines = self.request.split("\r\n")
		self.HTTP_information()
		# check API and protocol here
		self.check_API()
		if self.check_error():
			print("[Bad request]", self.error)
			return
		self.check_protocol()
		if self.check_error():
			print("[Bad request]", self.error)
			return


		if self.method == "POST":
			self.POST_request()
		elif self.method == "GET":
			self.GET_request()
		else:
			# method requested is not allowed
			self.error = 405
		if self.check_error():
			print("[Bad request]", self.error)
			return
		

# handle client requests
def handle_client(conn, addr):
	with conn:

		# determine if information is ready to receive from the socket
		
		# read data
		client_request = conn.recv(MAX_BUFFER).decode(FORMAT)
		# parse intial data transfer from the client
		request = HTTP_Parser(client_request, conn)
		request.parse_request()

		accept_message = "HTTP/1.1 200 OK\r\nHello\r\n\r\n"
		accept_message = accept_message.encode()
		conn.sendall(accept_message)
				
	print("[Closed connection]")

def main():
	print(ADDR)
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
		server.bind(ADDR)
		server.listen()
		while True:
			conn, addr = server.accept()
			handle_client(conn, addr)

if __name__ == "__main__":
	main()
