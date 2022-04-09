"""
An implementation of <tusclient.storage.interface.Storage>, using a file as storage.
"""
from tinydb import TinyDB, Query

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
        result = self._db.search(self._urls.key == key)
        return result[0].get('url') if result else None

    def set_item(self, key: str, url: str):
        """
        Store the url value under the unique key.

        :Args:
            - key[str]: The unique id to which the item (in this case, url) would be stored.
            - value[str]: The actual url value to be stored.
        """
        if self._db.search(self._urls.key == key):
            self._db.update({'url': url}, self._urls.key == key)
        else:
            self._db.insert({'key': key, 'url': url})

    def remove_item(self, key: str):
        """
        Remove/Delete the url value under the unique key from storage.
        """
        self._db.remove(self._urls.key==key)

    def close(self):
        """
        Close the file storage and release all opened files.
        """
        self._db.close()
