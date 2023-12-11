import unittest
import io

from tusclient.fingerprint import fingerprint


class FileStorageTest(unittest.TestCase):
    def setUp(self):
        self.fingerprinter = fingerprint.Fingerprint()

    def test_get_fingerpint(self):
        with open("./LICENSE", "rb") as f:
            content = f.read()
        buff = io.BytesIO()
        buff.write(content)
        buff.seek(0)  # reset buffer postion before reading

        with open("./LICENSE", "rb") as f:
            self.assertEqual(
                self.fingerprinter.get_fingerprint(buff), self.fingerprinter.get_fingerprint(f)
            )

    def test_unique_fingerprint(self):
        with open("./LICENSE", "rb") as f:
            content = f.read()
        buff = io.BytesIO()
        buff.write(content + b"s")  # add some salt to change value
        buff.seek(0)  # reset buffer postion before reading

        with open("./LICENSE", "rb") as f:
            self.assertNotEqual(
                self.fingerprinter.get_fingerprint(buff), self.fingerprinter.get_fingerprint(f)
            )
