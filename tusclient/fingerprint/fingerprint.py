"""
An implementation of of <tusclient.figerprint.interface.Figerprint>,
using the hashlib to generate an md5 hash based on the file content
"""
import hashlib

from . import interface


class Fingerprint(interface.Fingerprint):
    BLOCK_SIZE = 65536

    def get_fingerprint(self, fs):
        """
        Return a unique fingerprint string value based on the file stream recevied
        :Args:
            - fs[file]: The file stream instance of the file for which a fingerprint would be generated.
        :Returns: fingerprint[str]
        """
        hasher = hashlib.md5()
        buf = fs.read(self.BLOCK_SIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fs.read(self.BLOCK_SIZE)
        return hasher.hexdigest()
