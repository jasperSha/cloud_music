"""
Python server for clients to accees and upload their model.
"""

# imports
import socket
import server_model

# Constants
MAX_BUFFER = 1024
PORT = 9002
FORMAT = "utf-8"
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)

VALID_CALLS = {"/model/update": "POST", "/user/initialize": "GET", "/playlist": "GET"}

ERROR_RESPONSES = {400 : "HTTP/1.1 400 Bad Request\r\n\r\n", 404: "HTTP/1.1 404 Not Found\r\n\r\n",
    405: "HTTP/1.1 405 Method Not Allowed\r\n\r\n", 406: "HTTP/1.1 406 Not Acceptable\r\n\r\n"}

class HTTP_Parser:
	
	def __init__(self, client_request, conn):
		self.request = client_request
		self.lines = self.request.split("\r\n")
		self.socket = conn
		self.error = None
		self.method = None
		self.api_path = None
		self.protocol = None

	def get_method(self):
		return self.method
	
	def get_api_path(self):
		return self.api_path

	def get_protocol(self):
		return self.protocol

	def get_content(self):
		return self.lines[-1]

	def HTTP_information(self):
		"""
		input: None
		output: None
		purpose: seperate the http header and store for easier access
		"""
		request_line = self.lines[0].split()
		self.method = request_line[0]
		self.api_path = request_line[1]
		self.protocol = request_line[2]
	
	def contents(self):
		"""
		Unused
		"""
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
		"""
		input: None
		Output: bool
		purpose: check if there is error in the formating the request
		"""
		if self.error != None:
			 # make  instance of error class
			return True # to exit
		else:
			return False

	def check_API(self):
		"""
		input: None
		Output: None
		purpose: determine if API call is allowed by the server
		"""
		if self.api_path not in VALID_CALLS:
			self.error = 404
			return
		if self.method != VALID_CALLS[self.api_path]:
			self.error = 405
		
	def check_protocol(self):
		if self.protocol != "HTTP/1.1":
			self.error = 400


	def parse_request(self):
		"""
		Break down the user request by seperating into new lines
		"""
		self.HTTP_information()
		# check API and protocol here
		self.check_API()
		if self.check_error():
			return self.error

		self.check_protocol()
		if self.check_error():
			print("[Bad request]", self.error)
			return self.error

def GET_request(request, conn, model):
	"""
	input: User request -> request object, conn -> socket fd int, model -> server_model object
	Output: None
	purpose: Determine what was kind of get request was called and then perform the proper
	operation based on the request and send correct response back
	"""
	if request.get_api_path() == "/user/initialize":
		# get the nodes to send back to the client
		roots = model.get_best_roots()
		accept_message = "HTTP/1.1 200 OK\r\nContent-Length: 1485\r\n\r\n"
		for root in roots:
			accept_message += root + " "
		accept_message = accept_message.encode()
		conn.sendall(accept_message)
	else:
		content = request.get_content().split()
		# create playlist based off of client song_id
		print(content)
		playlist = server_model.get_neighbors(model.data, model.cluster_cols, content[0], int(content[1]), int(content[2]))
		accept_message = "HTTP/1.1 200 OK\r\nContent-Length: 1485\r\n\r\n"
		for song in playlist:
			accept_message += song + " "
		accept_message = accept_message.encode()
		conn.sendall(accept_message)

def POST_request(request, conn, model):
	"""
	input: client request
	output: None or -1
	purpose: given information from the client update  theserver model and send appropiate response
	"""
	content = request.get_content().split()
	songid = content[0]
	root_index = int(content[1])
	model.update_root(songid, root_index)
	# do something with the songid and index
	# based on update return values send proper response code
	accept_message = "HTTP/1.1 201 CREATED\r\n\r\n"
	accept_message = accept_message.encode()
	conn.sendall(accept_message)

# handle client requests
def handle_client(conn, addr, model):
	"""
	input: conn -> socket fd int, addr -> client addr, model -> server_model object 
	Output: None
	purpose: read initial request from the user, parse said request, direct said requeset to proper destination
	"""
	with conn:

		# determine if information is ready to receive from the socket
		# read data
		client_request = conn.recv(MAX_BUFFER).decode(FORMAT)
		print(client_request)
		# parse intial data transfer from the client
		request = HTTP_Parser(client_request, conn)
		result = request.parse_request()

		if result != None:
			message = ERROR_RESPONSES[result].encode()
			print(message)
			conn.sendall(message)
		if request.get_method() == "POST":
			code = POST_request(request, conn, model)
		elif request.get_method() == "GET":
			code = GET_request(request, conn, model)
		else:
			# method requested is not allowed
			print("error")
		
	print("[Closed connection]")

def main():
	# establish new server
	if server_model.check_model_exists("server_model.obj"):
		print("loading saved model")
		model = server_model.load_model("server_model.obj")
	else:
		print("creating new mdoel to begin with")
		knn_df, cluster_cols = server_model.load_data("fullmeta.csv")
		# current learning rate set to a high
		model = server_model.Server(knn_df, .5, cluster_cols)
		server_model.save_model(model)
	print(ADDR) 
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
		server.bind(ADDR)
		server.listen()
		while True:
			conn, addr = server.accept()
			handle_client(conn, addr, model)

if __name__ == "__main__":
	main()
 