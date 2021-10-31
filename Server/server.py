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

def post_request(client, request):
	"""
	Read file from the socket and write to local area
	"""
	

# parse request
def parsee_request(request):
	"""
	Break down the user request
	to use for later
	"""
	lines = request.split("\r\n")
	request_line = lines[0]
	method = request_line[0]
	path = request_line[1]
	protocol = request_line[2]
	return (method, path, protocol)


# handle client requests
def handle_client(conn, addr):
	with conn:
		# read data
		client_request = conn.recv(MAX_BUFFER).decode(FORMAT)
		print(client_request)
		header = parsee_request(client_request)
		if header[0] == "POST":
			post_request(conn, client_request)
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
