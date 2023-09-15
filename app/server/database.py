from pymongo import MongoClient

from dotenv import dotenv_values

# from config import settings

env_config = dotenv_values(".env")

# NOTE: connects to the mongo database here using MONGODB ATLAS so db is in the cloud
# mongo_client = MongoClient(settings.ATLAS_URI)
# print("Connected to MongoDB... Success!")

# db = mongo_client[settings.CLUSTER_DB_NAME]
# posts_coll = db[settings.POSTS_COLLECTION_NAME]
# users_coll = db[settings.USERS_COLLECTION_NAME]

mongo_client = MongoClient(f"{env_config['ATLAS_URI']}")
print("Connected to MongoDB... Success!")

db = mongo_client[f"{env_config['CLUSTER_DB_NAME']}"]
posts_coll = db[f"{env_config['POSTS_COLLECTION_NAME']}"]
users_coll = db[f"{env_config['USERS_COLLECTION_NAME']}"]
