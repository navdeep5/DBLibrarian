from pymongo import MongoClient, TEXT
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

def article_search(col):
	'''
	User is able to provide a list of keywords.
	Keywords are used to search for matches in any of title, authors, abstract, venue and year.
	Search is case insensitive.
	'''
	
	# drop indexes

	# col.drop_indexes()

	# create indexes
	# col.create_index([("title", "text"), ("authors", "text"), ("abstract", "text"),  ("venue", "text"),  ("year", "text")])


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
				boolList = []
				for n in range(len(key_words)):
					boolList.append(False)
				# matches = 0

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
						boolList[key_words.index(word)] = True
						# matches += 1
					if article["venue"] is not None and word.lower() in article["venue"].lower():
						boolList[key_words.index(word)] = True
						# matches += 1
					if word ==  str(article["year"]):
						boolList[key_words.index(word)] = True
						# matches += 1
					if abstract != "":
						if article["abstract"] is not None and word.lower() in article["abstract"].lower():
							boolList[key_words.index(word)] = True
							# matches += 1
					if any(word in s.lower() for s in article["authors"]):
						boolList[key_words.index(word)] = True
						# matches += 1

				# print(boolList)
				#if id != "" and title != "" and year != "" and venue != "" and matches >= len(key_words):
				if not boolList.__contains__(False):
					print(f"{i}: {id} | {title} | {year} | {venue}")
					results.append(article)
					i += 1
					inner_valid = True
				
				# if matches >= len(key_words):
				# 	print(f"{i}: {id} | {title} | {year} | {venue}")
				# 	results.append(article)
				# 	i += 1

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
						chosen_id = results[int(article_num)]["id"] if "id" in article else ""
						#print(chosen_id)
						here = col.find_one({"id": {"$eq": chosen_id}})
						here_title = here_year = here_venue = here_abstract = here_authors = "N/A"
						here_title = str(here["title"]) if "title" in here and here["title"] != []else "N/A"
						here_year = str(here["year"]) if "year" in here and here["year"] != [] else "N/A"
						here_venue = str(here["venue"]) if "venue" in here and here["venue"] != [] or here["venue"] != "" else "N/A"
						here_abstract = str(here["abstract"]) if "abstract" in here and here["abstract"] != [] else "N/A"
						here_authors = str(here["authors"]) if "authors" in here and here["authors"] != [] else "N/A"
						print("ID: " + chosen_id + "\nTitle: " + here_title + "\nYear: " + here_year + "\nAuthor(s): " + here_authors + "\nVenue(s): " + here_venue + "\nAbstract: " + here_abstract)
						#print(here)

						# display articles which reference this article
						print("\nHere are some articles that reference the article you picked:")
						found = False
						#referenced = col.aggregate({"$match": {"references": {"$regex": chosen_id}}})
						referenced = col.find({"references" : {"$in": [chosen_id]}})
						query = 1
						for match in referenced:
							reference_id = match["id"] if "id" in match is not None and "id" in match else ""
							reference_title = match["title"] if "title" in match is not None and "title" in match else ""
							reference_year = match["year"] if "year" in match is not None and "year" in match else ""
							
							print("---- " + str(query) + " ----")
							print(f"{reference_id} | {reference_title} | {reference_year}")
							query += 1
							found = True
						
						if not found:
							print("Oops... looks like this article has not been referenced.")
			else:
				print("No articles with matching keywords exists.\n Please try again!")


def author_search(col):
	'''
	User is able to provide a list of keywords.
	Keywords are used to search for matches in any of the authors' names
	Search is case insensitive.
	'''
	
	# DEBUG
	#print(col.count_documents({}))

	# index
	#col.drop_indexes()
	#col.create_index([("authors", "text")])
	#col.create_index([("title", "text"), ("authors", "text"), ("abstract", "text"),  ("venue", "text"),  ("year", "text")])

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
		#string_match = "(?i)" + keyword.strip() + "(?-i)"

		# create and run query
		# result = col.find({"authors": {"$regex": string_match}})
		# pipeline = [{"$project": {"authors": 1, "n_citation": 1, "_id": 0}}, {"$unwind": "$authors" }, {"$match": {"authors": {"$regex" : string_match}}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]
		# pipeline_2 = [{"$project": {"authors": 1, "n_citation": 1, "_id": 0}}, {"$match": {"authors": keyword}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]
		# pipeline_3 = [{"$project": {"authors": 1, "n_citation": 1, "_id": 0}}, {"$unwind": "$authors" }, {"$match": {"authors": keyword.strip()}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]
		# pipeline_4 = [{"$match": { "$text": {"$search": keyword}}}, {"$project": {"authors": 1, "n_citation": 1, "_id": 0}}, {"$unwind": "$authors" }, {"$match": {"authors": {"$regex" : string_match}}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]
		# pipeline_5 = [{"$match": { "$and":[{"$text": {"$search": keyword}}, {"authors": {"$regex" : string_match}}] }}, {"$project": {"authors": 1, "n_citation": 1, "_id": 0}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]
		# pipeline_6 = [{"$project": {"authors": 1, "n_citation": 1, "_id": 0}}, {"$match": {"authors": {"$elemMatch": keyword}}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]
		# pipeline_7 = [{"$unwind": "$authors"}, {"$match": {"authors": {"$regex": string_match, "$options": "i"}}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]
		# pipeline_8 = [{"$unwind": "$authors"}, {"$match": {"authors": {"$regex": string_match, "$options": "i"}}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]


		# display results
		intial = []
		# result = []
		# authors = []
		authors_dict = {}
		result_dict = {}
		#result = col.aggregate(pipeline_7)
		look = "/" + keyword + "/i"
		#result = col.find({"authors": look})
		intial = col.find({ "$text" : { "$search" : look, 
                          "$caseSensitive": False,
                          "$diacriticSensitive": True,
						  "$language": "none"}})

		for i in intial:
			author_list = i['authors']
			for person in author_list:
				name = person.replace("-", " ")
				name = name.split()

				# if keyword.lower() in person.lower():
				# 	if not person in result_dict:
				# 		result_dict[person] = 1
				# 	else:
				# 		result_dict[person] += 1
				for part in name:
					if keyword.lower() == part.lower():
						if not person in result_dict:
							result_dict[person] = 1
						else:
							result_dict[person] += 1
		
		

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
		# num = 1
		# for i in result:
		# 	print(str(num) + ") " + str(i))
		# 	result_dict[num] = i["_id"]
		# 	num += 1

		num = 1
		for indv in result_dict:
			print(str(num) + ") " + str(indv) + ", Number of Publications: " + str(result_dict[indv]))
			num += 1
		
		if len(result_dict) <= 0:
			print("*" * 30)
			print("There are no matched by the name of: " + keyword)
			print("Try again!")
			
		else:
			inner_valid = True
			# print("dict:" + str(result_dict))
			# print("size:" + str(len(result_dict)))
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

					# get list of authors
					authors_list = list(result_dict)
					# create and run query
					# pipeline_4 = [{"$project": {"authors": 1, "title": 1, "year": 1, "venue": 1, "_id": 0}}, {"$unwind": "$authors" }, {"$match": {"authors": result_dict[int(author)]}}, {"$group": {"_id": "$authors", "Number of Publications": {"$sum": 1}}}]
					# pipeline_5 = [{"$unwind": "$authors" }, {"$match": {"authors": result_dict[int(author)]}}, {
					# 	"$group": {"_id": "$authors", "Title": {"$push": "$title"}, "Year": {"$push": "$year"}, "Venue": {"$push": "$venue"}}
					# }, {"$sort":{"year": 1}}]
					# pipeline_6 = [{"$unwind": "$authors" }, {"$match": {"authors": result_dict[int(author)]}}, {
					# 	"$group": {"_id": "$_id", "Title": {"$push": "$title"}, "Year": {"$push": "$year"}, "Venue": {"$push": "$venue"}}
					# }, {"$sort":{"year": 1}}]
					pipeline_7 = [{"$unwind": "$authors" }, {"$match": {"authors": authors_list[int(author) - 1]}}, {
						"$group": {"_id": "$_id", "Title": {"$push": "$title"}, "Year": {"$push": "$year"}, "Venue": {"$push": "$venue"}, "Abstract": {"$push": "$abstract"}}
					}, {"$sort":{"Year": -1}}]
					# pipeline_7 = [{"$unwind": "$authors" }, {"$match": {"authors": authors_list[int(author) - 1]}}, {
					# 	"$group": {"_id": "$_id", "Count": {"$sum": 1} }
					# }, {"$sort":{"year": 1}}]


					result_2 = col.aggregate(pipeline_7)

					# display results
					for article in result_2:
						#print(article)
						#id = title = year = venue = abstract = "N/A"
						id = str(article["_id"]) if "_id" in article else "N/A"
						title = str(article["Title"][0]) if "Title" in article and article["Title"] != []else "N/A"
						year = str(article["Year"][0]) if "Year" in article and article["Year"] != []else "N/A"
						venue = str(article["Venue"]) if "Venue" in article and article["Venue"] != [] else "N/A"
						abstract = str(article["Abstract"]) if "Abstract" in article and article["Abstract"] != [] else "N/A"
						print("ID: " + id + "\nTitle: " + title + "\nYear: " + year + "\nVenue(s): " + venue + "\nAbstract: " + abstract)

def venue_list(db):
	'''
	1k
	{'_id': 'principles of knowledge representation and reasoning', 'totalReferences': 1}

	'''	

	os.system('cls||echo -e \\\\033c')

	while True:
		n = input("Input the number of top venues you would like to see:\n>>>")
		if not n.isdigit() or int(n) < 1:
			print("The number must be an integer greater than 0!")
			continue
		break
	n = int(n)
	assert (n > 0)

	col = db['view_total']
	pipeline = [
  	  { "$sort": {"_id.distinct_ref": -1}},
  	  { "$limit" : n}
	]

	venues = col.aggregate(pipeline)

	os.system('cls||echo -e \\\\033c')
	try:
		print("Printing venues in descending order . . .")
		print("-" * 100)
		for i in venues:
			print("Venue:",i['_id']['venue'],"| Times Cited:", i['_id']['distinct_ref'], "| Article Count:", i['count_articles']['count_articles'] )
		print("-" * 100)
	except IndexError:
		print("No venues to print!")

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