from pymongo import MongoClient, TEXT
import os
import sys
import subprocess
DEBUG = False
MAKE_VIEWS = True # Turn this to true when you want to run query 3

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

	if DEBUG:
		# printing all indexes for debugging purposes
		for i in col.index_information():
		 	print("Index: ",i)


	# loading the dblp collection from json file.
	cmd = "mongoimport --port=" + sys.argv[1] +" --db=291db --collection=dblp --file=" + jsonfile_name
	returned_value = subprocess.call(cmd, shell=True) 
	# exit code in unix 
	print('returned value', returned_value) # return value 0 means it is successful.

	col.drop_indexes()
	col.create_index([("references", 1)])
	col.create_index([("venue", 1)])
	col.create_index([("id", 1)])
	col.create_index([("authors", "text"), ("title", "text"), ("abstract", "text"), ("year", "text")])


	if 'count_articles' in collections:
		db['count_articles'].drop()
	if 'view_top_references' in collections:
		db['view_top_references'].drop()
	if 'view_total' in collections:
		db['view_total'].drop()




	
	# generating views: should take (~3-4 mins)
	if MAKE_VIEWS:

		# materialized view: "count_articles"
		
		pipeline = [
			{
			  "$group":
			  {
			  	"_id": "$venue",
			  	"count_articles": {"$count": {}}
			  }
			},
			{"$project": {"count_articles": 1, "_id": 1}},
			{"$merge": {"into": "count_articles", 'whenMatched': "replace"}}
		]
		col.aggregate(pipeline)


		# materialized view: 'view_top_references'
		pipeline = [
		  { "$project": {"_id": 0, "references": 1, "id": 1}},
		  { "$unwind": {"path": "$references"}},
		  {
		  	"$lookup":
		  	{
		  	  "from": "dblp",
	  	  	  "localField" : "references",	  # references
	  	  	  "foreignField" : "id", 	  	  # id
	  	  	  "as" : "ref_venue"
		  	}
		  },
		  { "$unwind": {"path": "$ref_venue"}},
		  { "$project": {"id": 1, "ref_venue.venue" :1}},

		  # stage : group by distinct references to venue.
		  {
		  	"$group":
		  	{
		  	  "_id": 
		  	  	{
	  	  		"venue" : "$ref_venue.venue",
	  	  		"id" : "$id"
		  	  	},
		  	}
		  }, 
		  { "$project": {"_id.venue" :1}},

		  {
		  	"$group":
		  	{
		  	  "_id": "$_id.venue",
		  	  "distinct_ref": {"$count": {}}
		  	}
		  },


		 {"$sort": {"distinct_ref": -1}},
		 {"$merge": {"into": "view_top_references", 'whenMatched': "replace"}}
	  	 ]

		col.aggregate(pipeline)
		# {'_id': 'Lecture Notes in Computer Science', 'distinct_ref': 48626}


		# materialized view: 'view_total'
		pipeline = [
		  { "$project": {"_id": 0, "venue": 1}},
		  { "$match" : {"$expr": {"$ne": ["$venue",'']}}}, # remove any empty venues

	  	  {
	  	  	"$lookup":
	  	  	{
	  	  	  "from" : "view_top_references",
	  	  	  "localField" : "venue",	  # venue
	  	  	  "foreignField" : "_id", 	# venue
	  	  	  "as" : "count_references" 
	  	  	}
	  	  },
	  	  { "$unwind": "$count_references"}, # count_references: {'_id': 'Lecture Notes in Computer Science', 'distinct_ref': 48626}
	  	  { "$project": {"venue": 1, "count_references.distinct_ref": 1}},

	  	  { 
	  	  	"$group":
	  	  	{
	  	  	  "_id": 
	  	  	  	{
	  	  		"venue" : "$venue",
	  	  		"distinct_ref" : "$count_references.distinct_ref"
		  	  	},
	  	  	}
	  	  },

	  	  { 
	  	  	"$lookup": 
	  	  	{
	  	  	  "from" : "count_articles",
	  	  	  "localField" : "_id.venue",   # venue
	  	  	  "foreignField" : "_id",		# venue
	  	  	  "as": "count_articles"
	  	  	}
	  	  },
	  	  { "$unwind": "$count_articles"}, # count_articles: {'_id'': venue, 'count_articles' : 1}
	  	  { "$project": {"_id": 1, "count_articles.count_articles": 1}},
	  	  { "$merge": {"into": "view_total", 'whenMatched': "replace"}}
		] 	
		col.aggregate(pipeline)





if __name__ == "__main__":
	main()