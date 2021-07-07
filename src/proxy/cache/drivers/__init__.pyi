from abc import ABCMeta, abstractmethod
from typing import Any

from bson import ObjectId
from pymongo.collection import Collection

class CacheDriver(metaclass=ABCMeta):

    @abstractmethod
    def cache_response(self, url: str, headers: bytes, body: bytes):
        ...

    @abstractmethod
    def delete_cached_response(self, url: str):
        ...

    @abstractmethod
    def get_cached_response(self, url: str) -> (bytes, bytes):
        ...


class MongoDBCacheDriver(CacheDriver):
    _collection: Collection

    def __init__(self, collection: Collection):
        ...

    @staticmethod
    def _get_object_id(value: Any) -> ObjectId:
        ...

    def cache_response(self, url: str, headers: bytes, body: bytes):
        ...

    def delete_cached_response(self, url: str):
        ...

    def get_cached_response(self, url: str) -> (bytes, bytes):
        ...
