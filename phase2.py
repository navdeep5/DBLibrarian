from pymongo import MongoClient
import os
import sys
import subprocess
# from sets import Set
import re
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
	client = MongoClient(port)

	return client

def article_search():
	'''
	User is able to provide a list of keywords.
	Keywords are used to search for matches in any of title, authors, abstract, venue and year.
	Search is case insensitive.
	'''
	pass

def author_search(col):
	'''
	User is able to provide a list of keywords.
	Keywords are used to search for matches in any of the authors' names
	Search is case insensitive.
	'''
	
	# DEBUG
	print(col.count_documents({}))

	# ask user for a keyword
	keyword = input("Enter a author keyword: ")

	# create and run query
	keyword = keyword.strip()
	string_match = "(?i)" + keyword.strip() + "(?-i)"
	# result = col.find({"authors": {"$regex": string_match}})

	pipeline = [{"$project": {"authors": 1, "n_citation": 1, "_id": 0}}, {"$match": {"authors": {"$regex" : string_match}}}]
	result = col.aggregate(pipeline)

	for i in result:
		print(i)

def venue_list(db):
	'''

	'''	
	col = db['dblp']

	os.system('cls||echo -e \\\\033c')

	while True:
		n = input("Input the number of top venues you would like to see:\n>>>")
		if not n.isdigit() or int(n) < 1:
			print("The number must be an integer greater than 0!")
			continue
		break
	n = int(n)

	pipeline = [
	  { "$project": {"_id": 0, "references": 1}},
	  { "$unwind": {"path": "$references"}},
	  
	  # left outer join:
	  {
	  	"$lookup": 
	  	{
	  	  "from" : "dblp",
	  	  "localField" : "references",
	  	  "foreignField" : "id",
	  	  "as": "referencing_venue"
	  	}
	  },


	  # stage : group by venue
	  {
	  	"$group":
	  	{
	  	  "_id": "$referencing_venue.venue",
	  	  "totalReferences": {"$count": {}} # count(*)
	  	}
	  },

	  {"$match" : {"$expr": {"$ne": ["$_id",[]]}}}, # remove references to no venues
	  {"$match" : {"$expr": {"$ne": ["$_id",['']]}}}, # remove empty venue names

	  { "$unwind": {"path": "$_id"}},
	  { "$sort": {"totalReferences": -1}},
  	  { "$limit" : n}
	]

	venues = col.aggregate(pipeline)
	# os.system('cls||echo -e \\\\033c')
	


	try:
		print("Printing venues in descending order . . .")
		print("-" * 120)
		for i in venues:
			print("Venue:",i['_id'],"| Times Cited:", i['totalReferences'], "| Article Count:", count_articles(db['dblp'], i['_id']))
	except IndexError:
		print("No venues to print!")

	# for i in venues:
	# 	print(i)
	return


def count_articles(col, venue):

	pipeline = [
	{
	  "$group":
	  {
	  	"_id": "$venue",
	  	"num_articles": {"$count": {}}
	  }
	},
	{"$match": {"$expr": { "$eq": ["$_id",venue] }}},
	{"$project": {"num_articles": 1, "_id": 0}}
	]

	num_articles = col.aggregate(pipeline)

	for i in num_articles:
		return(i['num_articles'])

	return
	



def checkUniqueness(id, col):
	'''
	check if id has already been used in the database.
	'''
	try:
		id = int(id)
	except Exception:
			return False
			
	results_count = col.count_documents({"id": id})
	if (results_count == 0):
		return True
	return False

def add_article(col):
	'''
	User is able to add an article to the collection.
	User provides a unique id, a title, a list of authors, and a year.
	'''
	unique = False
	while(not unique):
		id = input("Please enter a unique positive integer as the article id: ")
		unique = checkUniqueness(id, col)
		try:
			id = int(id)
		except Exception:
			unique = False
		if (not unique):
			print("\nInvalid id! Please try a different id.\n")

	title = input("Please enter a title for the article: ")

	authors = input("Please enter a one or many authors of the article seperated by commas: ")

	valid = False
	while(not valid):
		year = input("Please enter the publication year of the article: ")
		try:
			year = int(year)
			valid = True
		except Exception:
			valid = False

	authors_list = authors.split(',')
	try:
		article = {"id": int(id), "title": title, "authors": authors_list, "year": int(year), "abstract": None, "venue": None, "references": [], "n_citations": 0}
		col.insert_one(article)
		print("\nArticle added!\n")
	except Exception:
		print("\nArticle could not be added.\n")
		return


def main():

	# connecting to mongodb server
	client = connect(sys.argv[1]) # run server before connecting

	# connecting to database 291db 
	db_name = '291db' # phase 1 specs
	db = client[db_name] 


	# connecting to dblp collection where data has been previously loaded into
	col_name = 'dblp' # phase 1 specs
	col = db[col_name] 


	# display user options
	valid = True

	while valid:
		options = ["1) Search for article", "2) Search for authors", "3) List the venues", "4) Add an article", "'q' to quit."]
		print("*" * 30)
		print(" " * 11 + "User Menu")
		for option in options:
			print(option + "\n")
		print("Please select an option between 1 - 4.")
		print("*" * 30)
		user_option = input(">>>")

		# user input processing
		if user_option.isdigit() == False and bool(re.compile('q').search(user_option)):
			print("Goodbye!\n")
			return

		elif user_option.isdigit() == False:
			print("Invalid input! \nPlease enter a number between 1 - 4.")

		elif user_option.isdigit() and int(user_option) > 4:
			print("Invalid input " + str(user_option) + "!\nPlease ensure the value is less or equal to 4.")
		
		elif user_option.isdigit() and int(user_option) < 1:
			print("Invalid input " + str(user_option) + "!\nPlease ensure the value is greater or equal to 1.")
		
		elif int(user_option) == 1: # 1. search for articles - case insensitive
			article_search()
		
		elif int(user_option) == 2: # 1. search for authors - case insensitive
			author_search(col)
		
		elif int(user_option) == 3: # 1. list of venues
			venue_list(db)

		elif int(user_option) == 4: # 1. add article
			add_article(col)
	

if __name__ == "__main__":
	main()
