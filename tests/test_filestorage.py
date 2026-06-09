import unittest
import os

from tusclient.protocol_generated import url_storage_fingerprint_prefix
from tusclient.storage import filestorage


class FileStorageTest(unittest.TestCase):
    def setUp(self):
        self.storage_path = 'storage.json'
        self.storage = filestorage.FileStorage(self.storage_path)

    def tearDown(self):
        self.storage.close()
        os.remove(self.storage_path)

    def test_set_get_remove_item(self):
        url = 'http://tusd.tusdemo.net/files/unique_file_id'
        key = 'unique_key'

        url_2 = 'http://tusd.tusdemo.net/files/unique_file_id_2'
        key_2 = 'unique_key_2'
        self.storage.set_item(key, url)
        self.storage.set_item(key_2, url_2)

        self.assertEqual(self.storage.get_item(key), url)
        self.assertEqual(self.storage.get_item(key_2), url_2)
        self.assertEqual(self.storage.count(), 2)
        self.assertTrue(self.storage.keys()[0].startswith(url_storage_fingerprint_prefix(key)))
        self.assertTrue(self.storage.keys()[1].startswith(url_storage_fingerprint_prefix(key_2)))

        self.storage.set_item(key, url)
        self.assertEqual(self.storage.count(), 2)

        self.storage.remove_item(key)
        self.assertIsNone(self.storage.get_item(key))
