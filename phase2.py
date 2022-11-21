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
	client = MongoClient()

	return client

def article_search(col):
	'''
	User is able to provide a list of keywords.
	Keywords are used to search for matches in any of title, authors, abstract, venue and year.
	Search is case insensitive.
	'''
	
	# drop indexes
	col.drop_indexes()

	# create indexes
	col.create_index([("title", "text"), ("authors", "text"), ("abstract", "text"),  ("venue", "text"),  ("year", "text")])

	# create initial loop 
	valid = True
	inner_valid = True

	while valid:

		# ask user for keyboard
		print("Enter some keyword to search for an article.")
		print("Separate your keyword by a comma (',').")
		print("Or type b to return back to User Menu.")
		key_words_string = input(">>>")
		print("*" * 30)

		# input processing
		key_words = key_words_string.split(',')

		# data processing - ensure there are no uncessary white spaces
		for i in range(len(key_words)):
			key_words[i] = key_words[i].strip().lower()

		# check input
		if len(key_words) == 1:

			# return to User Menu
			if key_words[0] == 'b':
				valid = False
				return
		
		elif len(key_words) == 0:
			print("No words have been entered... Try again!")

		# write search query
		else:
			pipeline = {"$text": {"$search": f"{' '.join(key_words)}"}}
			results = []

			i = 0
			for article in col.find(pipeline):
				matches = 0

				id = article["id"] if "id" in article else ""
				title = article["title"] if "title" in article else ""
				year = article["year"] if "year" in article else ""
				venue = article["venue"] if "venue" in article else ""
				abstract = article["abstract"] if "abstract" in article else ""
				
				features = ["title", "venue", "year"]
				if abstract != "":
					features.append("abstract")

				# for part in features:
				# 	for word in key_words:
				# 		if word in str(article[part]):
				# 			#print(article[part])
				# 			matches += 1
				# for word_2 in key_words:
				# 	if any(word_2 in s for s in article["authors"]):
				# 		matches += 1
				# print(matches)

				
				for word in key_words:
					if word.lower() in article["title"].lower():
						matches += 1
					if word.lower() in article["venue"].lower():
						matches += 1
					if word ==  str(article["year"]):
						matches += 1
					if abstract != "":
						if word.lower() in article["abstract"].lower():
							matches += 1
					if any(word in s for s in article["authors"]):
						matches += 1

				#if id != "" and title != "" and year != "" and venue != "" and matches >= len(key_words):
				
				if matches >= len(key_words):
					print(f"{i}: {id} | {title} | {year} | {venue}")
					results.append(article)
					i += 1

				# allow user to learn more about an article 
			if len(results) > 0:
				while inner_valid:
					print("*" * 30)
					print("Enter the # of the article you want to know more about.")
					print("Or enter b to go back.")
					article_num = input(">>>")
					
					# input checking
					if article_num.strip() == "b":
						inner_valid = False
					elif article_num.isdigit() == False:
						print("Please enter a number.")
					elif article_num[0] == "-":
						print("Please enter a positive number.")
					elif article_num.isdigit() and int(article_num) > len(results) - 1:
						print("Please pick a number less than " + str(len(results) - 1) + ".")
					elif article_num.isdigit() and int(article_num) < 0:
						print("Please pick a number greater than 0.")
					else:

						# gather the chosen article
						chosen = results[int(article_num)]

						# present the full article information
						print("Here is more infromation about the article:")
						chosen_id = chosen["id"]
						info = col.find({"$match": {"id": chosen_id}})

						# display articles which reference this article
						print("Here are some articles that reference the article you picked:")
						for match in col.aggregate({"$unwind": "$references"}, {"$match": {"references": chosen_id}}):
							reference_id = match["id"] if "id" in match else ""
							reference_title = match["title"] if "title" in match else ""
							reference_year = match["year"] if "year" in match else ""
							
							print(f"{reference_id} | {reference_title} | {reference_year}")

def author_search(col):
	'''
	User is able to provide a list of keywords.
	Keywords are used to search for matches in any of the authors' names
	Search is case insensitive.
	'''
	
	# DEBUG
	print(col.count_documents({}))

	# index
	col.create_index([("authors", "text")])

	# create loop
	outer_valid = True
	inner_valid = True
	while outer_valid:

		# ask user for a keyword
		print("Enter a author keyword.")
		print("Or type b to return back to User Menu.")
		valid_input = True
		while valid_input:
			keyword = input(">>>")

			if keyword == "b":
				outer_valid = False
				valid_input = False
				return
			elif keyword.isdigit():
				print("Please enter a name!")
			else:
				valid_input = False

		# check user input
		keyword = keyword.strip()
		string_match = "(?i)" + keyword.strip() + "(?-i)"

		# create and run query
		# result = col.find({"authors": {"$regex": string_match}})
		pipeline = [{"$project": {"authors": 1, "n_citation": 1, "_id": 0}}, {"$unwind": "$authors" }, {"$match": {"authors": {"$regex" : string_match}}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]
		pipeline_2 = [{"$project": {"authors": 1, "n_citation": 1, "_id": 0}}, {"$match": {"authors": keyword}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]
		pipeline_3 = [{"$project": {"authors": 1, "n_citation": 1, "_id": 0}}, {"$unwind": "$authors" }, {"$match": {"authors": keyword.strip()}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]
		pipeline_4 = [{"$match": { "$text": {"$search": keyword}}}, {"$project": {"authors": 1, "n_citation": 1, "_id": 0}}, {"$unwind": "$authors" }, {"$match": {"authors": {"$regex" : string_match}}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]
		pipeline_5 = [{"$match": { "$and":[{"$text": {"$search": keyword}}, {"authors": {"$regex" : string_match}}] }}, {"$project": {"authors": 1, "n_citation": 1, "_id": 0}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]
		pipeline_6 = [{"$project": {"authors": 1, "n_citation": 1, "_id": 0}}, {"$match": {"authors": {"$elemMatch": keyword}}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]


		# display results
		result = []
		result_dict = {}
		result = col.aggregate(pipeline_6)

		# determine the number of results
		# if count <= 0:
		# 	print("*" * 30)
		# 	print("There are no matched by the name of:" + keyword)
		# 	print("Try again!")

		# else:
		# 	print("*" * 30)
		# 	num = 1
		# 	for i in result:
		# 		print(str(num) + ") " + str(i))
		# 		result_dict[num] = i["_id"]
		# 		num += 1

		print("*" * 30)
		num = 1
		for i in result:
			print(str(num) + ") " + str(i))
			result_dict[num] = i["_id"]
			num += 1
		
		if len(result_dict) <= 0:
			print("*" * 30)
			print("There are no matched by the name of: " + keyword)
			print("Try again!")
			
		else:
			print("dict:" + str(result_dict))
			print("size:" + str(len(result_dict)))
			while inner_valid:
				# The user should be able to select an author and see the title, year and venue of all articles by that author. 
				# The result should be sorted based on year with more recent articles shown first.

				# diplay user option
				print("*" * 30)
				print("Enter the # of the author you want to learn more about.")
				print("Or enter b to go back.")
				author = input(">>>")
				

				# Check user input	
				if author.strip() == "b":
					inner_valid = False
				elif author.isalpha():
					print("Please enter a number.")
				elif author[0] == "-":
					print("Please enter a positive number.")
				elif author.isdigit() and int(author) <= 0:
					print("The number you have entered is too low.")
				elif author.isdigit() and int(author) > len(result_dict):
					print("The number you have entered is too high.")	
				else:

					# create and run query
					pipeline_4 = [{"$project": {"authors": 1, "title": 1, "year": 1, "venue": 1, "_id": 0}}, {"$unwind": "$authors" }, {"$match": {"authors": result_dict[int(author)]}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]
					pipeline_5 = [{"$unwind": "$authors" }, {"$match": {"authors": result_dict[int(author)]}}, {
						"$group": {"_id": "$authors", "Title": {"$push": "$title"}, "Year": {"$push": "$year"}, "Venue": {"$push": "$venue"}}
					}, {"$sort":{"year": 1}}]
					pipeline_6 = [{"$unwind": "$authors" }, {"$match": {"authors": result_dict[int(author)]}}, {
						"$group": {"_id": "$_id", "Title": {"$push": "$title"}, "Year": {"$push": "$year"}, "Venue": {"$push": "$venue"}}
					}, {"$sort":{"year": 1}}]


					result_2 = col.aggregate(pipeline_6)

					# display results
					for i in result_2:
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

	# create index for purpose of searching 
	'''
	col.create_index([("title", "text"), ("authors", "text"), ("abstract", "text"),  ("venue", "text"),  ("year", "text")])
	'''
	#db.col.createIndex({"authors": "text", "title": "text", "references": "text", "venue":"text"})
	#col.create_index([('authors', pymongo.TEXT)], name='search_index', default_language='english')
	#col.create_index("authors", unique = True)

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
			article_search(col)
		
		elif int(user_option) == 2: # 1. search for authors - case insensitive
			author_search(col)
		
		elif int(user_option) == 3: # 1. list of venues
			venue_list(db)

		elif int(user_option) == 4: # 1. add article
			add_article(col)
	

if __name__ == "__main__":
	main()