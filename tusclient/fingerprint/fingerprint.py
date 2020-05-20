"""
An implementation of of <tusclient.figerprint.interface.Figerprint>,
using the hashlib to generate an md5 hash based on the file content
"""
from typing import IO
import hashlib
import os

from . import interface


class Fingerprint(interface.Fingerprint):
    BLOCK_SIZE = 65536

    def get_fingerprint(self, fs: IO):
        """
        Return a unique fingerprint string value based on the file stream recevied

        :Args:
            - fs[IO]: The file stream instance of the file for which a fingerprint would be generated.
        :Returns: fingerprint[str]
        """
        hasher = hashlib.md5()
        # we encode the content to avoid python 3 uncicode errors
        buf = self._encode_data(fs.read(self.BLOCK_SIZE))
        hasher.update(buf)
        # add in the file size to minimize chances of collision
        fs.seek(0, os.SEEK_END)
        file_size = fs.tell()
        return 'size:{}--md5:{}'.format(file_size, hasher.hexdigest())

    def _encode_data(self, data):
        try:
            return data.encode('utf-8')
        except AttributeError:
            # in case the content is already binary, this failure would happen.
            return data
