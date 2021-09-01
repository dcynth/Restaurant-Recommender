from pymongo import MongoClient
client = MongoClient("mongodb+srv://cs411:project@cluster0-1yfcs.mongodb.net/test?retryWrites=true&w=majority")
db = client.get_database('users_db')
records = db.profiles
print(records.count_documents({}))
