from pymongo import MongoClient
from config.settings import settings


client = MongoClient(settings.mongo_uri)

db = client[settings.database_name]


def get_database():
    return db