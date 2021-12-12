"""
Client program to test along side with server
"""
import socket
import os
import client_model

# Constants
PORT =  9002
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)
MAX_BUFFER = 2048
FORMAT = "utf-8"

def play_playlist(playlist):
	"""
	input: playlist - list of songs for the user to input
	output: list of songs that have rating like, dislike, neutral
	purpose: display songs from the playlist and prompt the user to get their interaction
	"""
	
	responses = []
	previous_input = ""
	for song in playlist:
		os.system("clear")
		print(previous_input, end="")
		user_input = input(f"What did you think about {song}: [L, D, N]: ")
		while True:
			if user_input.upper() == 'L':
				responses.append(1)
				previous_input += song + " LIKE\n"
				break
			elif user_input.upper() == 'D':
				responses.append(-1)
				previous_input += song + " DISLIKE\n"
				break
			elif user_input.upper() == 'N':
				responses.append(0)
				previous_input += song + " Nuetral\n"
				break
			else:
				print("Error: none proper input given please input L for like, D for dislike, or N for nuetral")
				user_input = input(f"What did you think about {song}: [L, D, N]: ")
	os.system("clear")
	print(previous_input)
	return responses

def initialize_user():
	message = "GET /user/initialize HTTP/1.1\r\n\r\n"
	msg = message.encode(FORMAT)

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect(ADDR)
			response = send_message(s, msg)
			if response is not None:
				# do something to initiaze the user
				return client_model.User(response)
			else:
				return -1

def update_model(songid, root_index):

	# for update the model songid and index number
	message = "POST /model/update HTTP/1.1\r\nContent-Length: 15\r\n\r\n"	
	message += songid + " " + str(root_index)
	# add necassary song_ids
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

def get_playlist(user):
	# we need to get node, k lower and k
	# call request batch to get necassary info
	# takes user object, max_batch = 10
	request_node, k, k_lower = user.request_batch(10) 
	message = "GET /playlist HTTP/1.1\r\nContent-Length:15\r\n\r\n"
	message += request_node.get_id() + " " + str(k) + " " + str(k_lower)
	msg = message.encode(FORMAT)

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect(ADDR)
			playlist = send_message(s, msg)
			if playlist is not None:
				# do something with the playlist received
				print(playlist)
			else:
				# there was an error updating the model
				return -1
	# call filter with original node and list of songids from the server
	batch = user.filter_batch(request_node, playlist)
	# feedback for every song
	if batch is not None:
		feed_back = play_playlist(batch)
		# evaluate batch update user model
		evaluation = user.evaluate_batch(feed_back)
		# return whether update to server is needed
		if evaluation is not None:
			print("Updating model")
			update_model(evaluation[1], evaluation[0])

			

def handle_error(error):
	print(f"Received {error.split()[1:]} from the server")

def handle_response(r):
	#split the response into managable pieces
	response_parsed = r.split("\r\n\r\n")
	if len(response_parsed) > 1:
		# we know this will be ok because there is a content length
		response_header = response_parsed[0]
		response_content = response_parsed[1]
		return response_content.split() # returns list of song ids
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
	if response is None:
		print("Error: failed connection from server")
		return
	return handle_response(response)

def main():
	# when program first runs we immediately initialize a new user
	user_object = initialize_user()
	if user_object == -1:
		print("Error generating the user object")
		user_input = input("Woudl you like to try again?: ")
		while user_input != 'N':
			user_object = initialize_user()
			if user_object == -1:
				print("Error generating the user object")
				user_input = input("Woudl you like to try again? Y/N: ")
		if user_input == "N":
			return
	
	user_input = input("""What would you like to do?
[1] Get a playlist from the server?
[2] Quit: """)


	while user_input != "2":
		if user_input == "1":
			get_playlist(user_object) # pass user
		else:
			print("User error please input a number to select option")
		user_input = input("""What would you like to do?
[1] Get a playlist from the server?
[2] Quit: """)
	os.system("clear")
		


if __name__ == "__main__":
	user_input = input("What  would you like to do?\n[1] Test play_plalsit\n[2] Simulate User\n[3] Quit: ")
	while user_input != "3":
		if user_input == "1":
			value = play_playlist(["12345", "123456", "234"])
			print(value)
		elif user_input == "2":
			main()
			break
		else:
			print("User error please input a number to select option")
		user_input = input("What  would you like to do?\n[1] Test play_plalsit\n[2] Simulate User\n[3] Quit: ")
	os.system("clear")
	