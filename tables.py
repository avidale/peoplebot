import os
import pymongo

MONGO_URL = os.environ.get('MONGODB_URI')
mongo_client = pymongo.MongoClient(MONGO_URL)
mongo_db = mongo_client.get_default_database()

# chat_id -> chat_name
chats = mongo_db.get_collection('chats')

# chat_id, user_id
peoplebook = mongo_db.get_collection('peoplebook')

# chat_id, user_id
membership = mongo_db.get_collection('chat_membership')

# user_id
user_state = mongo_db.get_collection('user_state')
