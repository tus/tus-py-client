import io
import unittest

from parametrize import parametrize

from tusclient.fingerprint import fingerprint

FILEPATH_TEXT = "tests/sample_files/text.txt"
FILEPATH_BINARY = "tests/sample_files/binary.png"


class FileStorageTest(unittest.TestCase):
    def setUp(self):
        self.fingerprinter = fingerprint.Fingerprint()

    @parametrize(
        "filename",
        [FILEPATH_TEXT, FILEPATH_BINARY],
    )
    def test_get_fingerpint(self, filename: str):
        with open(filename, "rb") as f:
            content = f.read()
        buff = io.BytesIO()
        buff.write(content)
        buff.seek(0)  # reset buffer postion before reading

        with open(filename, "rb") as f:
            self.assertEqual(
                self.fingerprinter.get_fingerprint(buff),
                self.fingerprinter.get_fingerprint(f)
            )

    @parametrize(
        "filename",
        [FILEPATH_TEXT, FILEPATH_BINARY],
    )
    def test_unique_fingerprint(self, filename: str):
        with open(filename, "rb") as f:
            content = f.read()
        buff = io.BytesIO()
        buff.write(content + b's')  # add some salt to change value
        buff.seek(0)  # reset buffer postion before reading

        with open(filename, "rb") as f:
            self.assertNotEqual(
                self.fingerprinter.get_fingerprint(buff),
                self.fingerprinter.get_fingerprint(f)
            )
