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


	# creating database 291db if it does not exist
	databases = client.list_database_names()
	db_name = '291db' # phase 1 specs
	db = client[db_name] # will create a new database if it doesnt exist.


	# creating our dblp collection if it does not exist
	collections = db.list_collection_names()
	col_name = 'dblp' # phase 1 specs
	if col_name in collections:
		col = db[col_name]
		dropped = col.drop() # col.drop() returns 1 if the collection was dropped successfully
		#assertion bug: assert(dropped) 
	col = db[col_name] 


	# conceptual structure of json file
	'''
	{"abstract": string, "authors": [], "n_citation": integer, "references": [], "title": string, "venue": string, "year": integer, "id": string, }
	
	abstract is optional, there are cases with it and cases without it.
	"authors": [string] - list of authors
	"references": [string] - list of references, each references are strings. an example of a reference. "51c7e02e-f5ed-431a-8cf5-f761f266d4be"

	'''

	# loading the dblp collection from json file.
	cmd = "mongoimport --db=291db --collection=dblp --file=" + jsonfile_name
	returned_value = subprocess.call(cmd, shell=True) 
	# exit code in unix 
	print('returned value', returned_value) # return value 0 means it is successful.














if __name__ == "__main__":
	main()