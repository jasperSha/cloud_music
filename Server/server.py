"""
Python server for clients to accees and upload their model.
"""

# import
import socket
import threading

# Constants
MAX_BUFFER = 1024
HEADER = 64
PORT = 9002
FORMAT = "utf-8"
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)


# POST
def process_post(conn, addr):
	print(f"[{addr}: POST]")

	# get msg_len
	msg_len = conn.recv(HEADER).decode(FORMAT)
	if not msg_len:
		# return error
		pass
	else:
		msg_len = int(msg_len)
		msg = conn.recv(msg_len).decode(FORMAT)
		msg = msg.split()
		file_name = msg[0]
		file_length = msg[1]

		print(f"[{addr}: {file_name} {file_length}]")

	# get file name and file length

	# write the file

# handle client requests
def handle_client(conn, addr):
	with conn:
		print(f"[New connection...{addr}]")
		connected = True
		while connected:
			#get length of initial message
			msg_len = conn.recv(HEADER).decode(FORMAT)
			if not msg_len:
				#client disconnected
				connected = False
			else:
				msg_len = int(msg_len)
				msg = conn.recv(msg_len).decode(FORMAT)
				if msg == 'POST':
					process_post(conn, addr)

				
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
