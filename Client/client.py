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
	"""
	input: None 
	output: user object if succesful or -1 if failed
	purpose: Creates a user object after receiving list of centroids from the server
	"""
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
	"""
	input: songid -> string, root_index: number associated with cluster
	output: None if got the ok from the server or -1 if recveived error
	purpose: Send server proper information to update the server model
	"""
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
	"""
	input: user -> user object 
	output: -1 if error, or None
	purpose: users gets proper information from the tree they have created, to communicate with the server
	which song they would like their playlist to be based off of and how large the playlist should be. Communicates
	with the server and gets a list of song ids back.  The playlist is then filtered to remove any duplicates, and 
	checks whether after the filter there is any songs to 'play'.  If not the user then requests for another batch.
	If there are songs for the user to listen to, the program will play the playlist and get feedback from the user.
	The client then evaluates based on the feedback whether it is necessary to send an update to the server.
	"""
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
	if batch != []:
		feed_back = play_playlist(batch)
		# evaluate batch update user model
		evaluation = user.evaluate_batch(feed_back)
		user.add_songs_to_set(batch)
		# return whether update to server is needed
		if evaluation is not None:
			print("Updating model")
			update_model(evaluation[1], evaluation[0])
	else:
		get_playlist(user)

def print_root_list(user):
	"""
	input: user object
	output: None
	purpose: print the user's root list to see how changes are being made to the server
	"""
	for song in user.root_list:
		print(song.get_id(), end =" ")

	print()			

def handle_error(error):
	print(f"Received {error.split()[1:]} from the server")

def handle_response(r):
	"""
	input: r -> string, response from server 
	output: returns None if an error was received from the server otherwise returns ok
	purpose: Properly parse the response from the server adquetly determining if there was an error received
	"""
	#split the response into managable pieces
	response_parsed = r.split("\r\n\r\n")
	if len(response_parsed) > 1:
		# we know this will be ok because there is a content length
		response_header = response_parsed[0]
		response_content = response_parsed[1]
		return response_content.split() # returns list of song ids
	else:
		if int(response_parsed[1]) >= 400:
			handle_error(response_parsed)
			return None
		else:
			return "ok"

def send_message(server, msg):
	"""
	input: server -> address to the server, msg -> string to send to the server 
	output: None if the there is no response from the server, returns the desired information from the server response
	purpose: communicates with the server and returns the desired information back to calling function
	"""
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
[2] Pring your current root list?
[3] Quit: """)


	while user_input != "3":
		if user_input == "1":
			get_playlist(user_object) # pass user
		elif user_input == "2":
			print_root_list(user_object)
		else:
			print("User error please input a number to select option")
		user_input = input("""What would you like to do?
[1] Get a playlist from the server?
[2] Pring your current root list?
[3] Quit: """)

	os.system("clear")
		


if __name__ == "__main__":
	user_input = input("What  would you like to do?\n[1] Test play_plalsit\n[2] Simulate User\n[3] Test Update Model" + 
	"\n[4] Quit: \n")
	while user_input != "4":
		if user_input == "1":
			value = play_playlist(["12345", "123456", "234"])
			print(value)
		elif user_input == "2":
			main()
			break
		elif user_input == "3":
			print(update_model("MCEcWcIww5k", 0))
		else:
			print("User error please input a number to select option")
		user_input = input("What  would you like to do?\n[1] Test play_plalsit\n[2] Simulate User\n[3] Quit: ")
	os.system("clear")
	