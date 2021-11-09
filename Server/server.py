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

class HTTP_Parser:
	
	def __init__(self, client_request):
		self.request = client_request
		self.error = None


	def HTTP_information(self):
		request_line = self.lines[0].split()
		self.method = request_line[0]
		self.api_path = request_line[1]
		self.protocol = request_line[2]

	def POST_request(self):
		if "Content-Length" in self.requets:
			index =  self.lines.find("Content-Length")
		else:
			print("Here")
			self.error  = 400
			return
		print(index)

	def GET_request(self):
		pass

	def parse_request(self):
		"""
		Break down the user request by seperating into new lines
		"""
		self.lines = self.request.split("\r\n")
		self.HTTP_information()
		if self.method == "POST":
			self.POST_request()
		elif self.method == "GET":
			self.GET_request()
		else:
			# method requested is not allowed
			self.error = 405

# handle client requests
def handle_client(conn, addr):
	with conn:

		# determine if information is ready to receive from the socket
		
		# read data
		client_request = conn.recv(MAX_BUFFER).decode(FORMAT)
		# parse intial data transfer from the client
		request = HTTP_Parser(client_request)
		request.parse_request()


		# determine all of the data needed to read from the client
		while len(client_request) == MAX_BUFFER:
			# print request
			#print(client_request)
			client_request = conn.recv(MAX_BUFFER).decode(FORMAT)
			
			"""header = parsee_request(client_request)
			if header[0] == "POST":
				post_request(conn, client_request)
			"""
		#print(client_request)
		accept_message = "HTTP/1.1 200 OK\r\nHello\r\n\r\n"
		accept_message = accept_message.encode()
		conn.sendall(accept_message)
		print("sent")

				
	print("[Closed connection]")

def main():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
		server.bind(ADDR)
		server.listen()
		while True:
			conn, addr = server.accept()
			handle_client(conn, addr)

if __name__ == "__main__":
	main()
