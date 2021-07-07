from abc import ABCMeta, abstractmethod
from hashlib import shake_128

from bson import ObjectId

__all__ = (
    'CacheDriver',
    'MongoDBCacheDriver',
)


class CacheDriver(metaclass=ABCMeta):
    @abstractmethod
    def get_cached_response(self, url):
        raise NotImplementedError

    @abstractmethod
    def cache_response(self, url, headers, body):
        raise NotImplementedError

    @abstractmethod
    def delete_cached_response(self, url):
        raise NotImplementedError


class MongoDBCacheDriver(CacheDriver):
    def __init__(self, collection):
        self._collection = collection

    @staticmethod
    def _get_object_id(value):
        # TODO: Doesn't follow the ObjectId specification but meh. See \
        #  <https://docs.mongodb.com/v5.0/reference/method/ObjectId/>.
        return ObjectId(shake_128(str(value).encode()).digest(12))

    def cache_response(self, url, headers, body):
        self._collection.update_one(
            {'_id': self._get_object_id(url)},
            {headers: headers, body: body},
            upsert=True,
        )

    def delete_cached_response(self, url):
        self._collection.delete_one({'_id': self._get_object_id(url)})

    def get_cached_response(self, url):
        document = self._collection.find_one({
            '_id': self._get_object_id(url),
        })

        return document['headers'], document['body']
