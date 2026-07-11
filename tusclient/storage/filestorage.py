"""
An implementation of <tusclient.storage.interface.Storage>, using a file as storage.
"""
from random import random

from tinydb import TinyDB, Query

from tusclient.protocol_generated import (
    url_storage_fingerprint_prefix,
    url_storage_id,
    url_storage_key,
)

from . import interface


class FileStorage(interface.Storage):
    def __init__(self, fp):
        self._db = TinyDB(fp)
        self._urls = Query()

    def get_item(self, key: str):
        """
        Return the tus url of a file, identified by the key specified.

        :Args:
            - key[str]: The unique id for the stored item (in this case, url)
        :Returns: url[str]
        """
        result = self._records_for_item(key)
        return result[0].get("url") if result else None

    def set_item(self, key: str, url: str):
        """
        Store the url value under the unique key.

        :Args:
            - key[str]: The unique id to which the item (in this case, url) would be stored.
            - value[str]: The actual url value to be stored.
        """
        result = self._records_for_item(key)
        if result:
            self._db.update({"url": url}, self._urls.key == result[0].get("key"))
        else:
            self._db.insert({"key": self._new_storage_key(key), "url": url})

    def remove_item(self, key: str):
        """
        Remove/Delete the url value under the unique key from storage.
        """
        for stored_key in self._keys_for_item(key):
            self._db.remove(self._urls.key == stored_key)

    def close(self):
        """
        Close the file storage and release all opened files.
        """
        self._db.close()

    def count(self):
        return len(self._db.all())

    def keys(self):
        return [record.get("key") for record in self._db.all()]

    def _records_for_item(self, key: str):
        exact = self._db.search(self._urls.key == key)
        if exact:
            return exact

        prefix = url_storage_fingerprint_prefix(key)
        return self._db.search(
            self._urls.key.test(
                lambda stored_key: isinstance(stored_key, str) and stored_key.startswith(prefix)
            )
        )

    def _keys_for_item(self, key: str):
        return [record.get("key") for record in self._records_for_item(key)]

    def _new_storage_key(self, key: str):
        return url_storage_key(key, url_storage_id(random()))
