from pymongo import MongoClient
import os
import sys
import subprocess
DEBUG = True

def connect(port_no):
	''' 
	Connects the program to a mongodb server specified by the user
	The command line arguments are expected to be:
		python3 load-json.py port_no jsonfile_name
		
	parameters:
	port_no (integer) : default port number for mongodb is 27017
	'''

	port = 'mongodb://localhost:' + port_no
	client = MongoClient()

	return client

def article_search():
	'''
	User is able to provide a list of keywords.
	Keywords are used to search for matches in any of title, authors, abstract, venue and year.
	Search is case insensitive.
	'''
	pass

def author_search():
	'''
	User is able to provide a list of keywords.
	Keywords are used to search for matches in any of the authors' names
	Search is case insensitive.
	'''
	pass

def venue_list():
	'''
	User is able to enter a number 'n'.
	Result will include a list of the top 'n' venues.
	For each venue, result will contain: the venue, the number of articles in that venue, and the number of articles that reference a paper in that venue.
	Results will be ordered based on the number of papers that reference the venue.
	Results will also be ordered such that venues in the top cities are shown first.
	'''
	pass

def add_article():
	'''
	User is able to add an article to the collection.
	User provides a unique id, a title, a list of authors, and a year.
	'''
	pass

def main():

	# connecting to mongodb server
	try:
		client = connect(sys.argv[1]) # run server before connecting
		jsonfile_name = sys.argv[2]	# file is assumed to be in the current directory. Under specifications, Phase 1.
	except IndexError:
		print("You must pass the port number when running this program")
		print("Example usage: ")
		print("python3 phase2.py port_no\n")
		quit()


	# connecting to database 291db 
	db_name = '291db' # phase 1 specs
	db = client[db_name] 


	# connecting to dblp collection where data has been previously loaded into
	col_name = 'dblp' # phase 1 specs
	col = db[col_name] 


	# display user options
	valid = True

	while valid:
		options = ["1) Search for article", "2) Search for authors", "3) List the venues", "4) Add an article"]
		print("*" * 30)
		print(" " * 11 + "User Menu")
		for option in options:
			print(option + "\n")
		print("Please select an option between 1 - 4.")
		print("*" * 30)
		user_option = input(">>>")

		# user input processing
		if user_option.isdigit() == False:
			print("Invalid input! \nPlease enter a number between 1 - 4.")

		elif user_option.isdigit() and int(user_option) > 4:
			print("Invalid input " + str(user_option) + "!\nPlease ensure the value is less or equal to 4.")
		
		elif user_option.isdigit() and int(user_option) < 1:
			print("Invalid input " + str(user_option) + "!\nPlease ensure the value is greater or equal to 1.")
		
		elif int(user_option) == 1: # 1. search for articles - case insensitive
			article_search()
		
		elif int(user_option) == 2: # 1. search for authors - case insensitive
			author_search()
		
		elif int(user_option) == 3: # 1. list of venues
			venue_list()
		
		elif int(user_option) == 4: # 1. add article
			add_article()
	

if __name__ == "__main__":
	main()