import mock
import pycurl

from tusclient import client, request
from tests import mixin


class TusRequestTest(mixin.Mixin):
    def setUp(self):
        super(TusRequestTest, self).setUp()
        self.request = request.TusRequest(self.uploader)

    def test_class_instance(self):
        self.assertIsInstance(self.request.handle, pycurl.Curl)

    def test_perform(self):

        with mock.patch.object(self.request, 'handle') as mock_:
            self.request.handle = mock_
            self.request.perform()
        mock_.perform.assert_called_with()

    def test_close(self):
        with mock.patch.object(self.request, 'handle') as mock_:
            self.request.handle = mock_
            self.request.close()
        mock_.close.assert_called_with()
