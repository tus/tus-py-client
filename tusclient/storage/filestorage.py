from tinydb import TinyDB, Query

from . import interface


class FileStorage(interface.Storage):
    def __init__(self, fp):
        self._db = TinyDB(fp)
        self._urls = Query()

    def get_item(self, key):
        result = self._db.search(self._urls.key == key)
        return result[0].get('url') if result else None

    def set_item(self, key, url):
        if self._db.search(self._urls.key == key):
            self._db.update({'url': url}, self._urls.key == key)
        else:
            self._db.insert({'key': key, 'url': url})

    def remove_item(self, key):
        self._db.remove(self._urls.key==key)
