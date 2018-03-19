"""
Interface module defining a url storage API.
"""
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class Storage(object):
    @abc.abstractmethod
    def get_item(self, key):
        """
        Return the tus url of a file, identified by the key specified.

        :Args:
            - key[str]: The unique id for the stored item (in this case, url)
        :Returns: url[str]
        """
        pass

    @abc.abstractmethod
    def set_item(self, key, value):
        """
        Store the url value under the unique key.

        :Args:
            - key[str]: The unique id to which the item (in this case, url) would be stored.
            - value[str]: The actual url value to be stored.
        """
        pass

    @abc.abstractmethod
    def remove_item(self, key):
        """
        Remove/Delete the url value under the unique key from storage.
        """
        pass
