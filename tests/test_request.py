import mock

from tusclient import client, request
from tests import mixin


class TusRequestTest(mixin.Mixin):
    def setUp(self):
        super(TusRequestTest, self).setUp()
        self.request = request.TusRequest(self.uploader)

    def test_perform(self):

        with mock.patch.object(self.request, 'handle') as mock_:
            self.request.handle = mock_
            self.request.perform()
        with open('LICENSE', 'rb') as f:
            headers = {
                'upload-offset': 0,
                'Content-Type': 'application/offset+octet-stream'
            }
            headers.update(self.uploader.headers)
            mock_.request.assert_called_with(
                'PATCH', '/files/15acd89eabdf5738ffc',
                f.read(), headers)

    def test_close(self):
        with mock.patch.object(self.request, 'handle') as mock_:
            self.request.handle = mock_
            self.request.close()
        mock_.close.assert_called_with()
