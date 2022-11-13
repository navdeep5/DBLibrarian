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

def main():

	# connecting to mongodb server
	try:
		client = connect(sys.argv[1]) # run server before connecting
		jsonfile_name = sys.argv[2]	# file is assumed to be in the current directory. Under specifications, Phase 1.
	except IndexError:
		print("You must pass the port number and json file name when running this program")
		print("Example usage: ")
		print("python3 load-json.py port_no jsonfile_name\n")
		quit()


	# connecting to database 291db 
	db_name = '291db' # phase 1 specs
	db = client[db_name] 


	# connecting to dblp collection where data has been previously loaded into
	col_name = 'dblp' # phase 1 specs
	col = db[col_name] 


	# 1. search for articles - case insensitive.

