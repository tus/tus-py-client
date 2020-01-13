import mock
import base64
import hashlib

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
                'upload-offset': '0',
                'Content-Type': 'application/offset+octet-stream'
            }
            headers.update(self.uploader.headers)
            mock_.patch.assert_called_with(
                'http://master.tus.io/files/15acd89eabdf5738ffc',
                data=f.read(), headers=headers)

    def test_perform_checksum(self):
        self.uploader.upload_checksum = True
        self.request_checksum = request.TusRequest(self.uploader)
        with mock.patch.object(self.request_checksum, 'handle') as mock_:
            self.request_checksum.handle = mock_
            self.request_checksum.perform()
        with open('LICENSE', 'rb') as f:
            license = f.read()
            headers = {
                'upload-offset': '0',
                'Content-Type': 'application/offset+octet-stream'
            }
            headers.update(self.uploader.headers)
            headers["upload-checksum"] = "sha1 " + \
                base64.standard_b64encode(hashlib.sha1(license).digest()).decode("ascii")
            mock_.patch.assert_called_with(
                'http://master.tus.io/files/15acd89eabdf5738ffc',
                data=license, headers=headers)

    def test_close(self):
        with mock.patch.object(self.request, 'handle') as mock_:
            self.request.handle = mock_
            self.request.close()
        mock_.close.assert_called_with()
