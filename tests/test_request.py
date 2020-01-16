import base64
import hashlib

import mock
import requests_mock

from tusclient import request
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

    @requests_mock.Mocker()
    def test_perform_checksum(self, mocked_request):
        self.uploader.upload_checksum = True
        tus_request = request.TusRequest(self.uploader)

        with open('LICENSE', 'r') as f:
            license_ = f.read()
            headers = {
                'upload-offset': '0',
                'Content-Type': 'application/offset+octet-stream'
            }
            encoded_file = license_.encode('utf-8')
            headers.update(self.uploader.headers)
            headers["upload-checksum"] = "sha1 " + \
                base64.standard_b64encode(hashlib.sha1(encoded_file).digest()).decode("ascii")
            mocked_request.patch(
                'http://master.tus.io/files/15acd89eabdf5738ffc',
                text=license_, request_headers=headers)
            tus_request.perform()
