import abc, six


@six.add_metaclass(abc.ABCMeta)
class Storage(object):
    @abc.abstractmethod
    def get_item(self, key):
        pass

    @abc.abstractmethod
    def set_itme(self, key, value):
        pass

    @abc.abstractmethod
    def remove_item(self, key):
        pass
