from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

__all__ = ('collection',)

# TODO: replace with config file
# TODO: close connection
client = MongoClient()
db = client.proxy_server  # type: Database
collection = db.cache  # type: Collection
