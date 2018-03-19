"""
Interface module defining a fingerprint generator based on file content.
"""
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class Fingerprint(object):
    @abc.abstractmethod
    def get_fingerprint(self, fs):
        """
        Return a unique fingerprint string value based on the file stream recevied

        :Args:
            - fs[file]: The file stream instance of the file for which a fingerprint would be generated.
        :Returns: fingerprint[str]
        """
        pass
