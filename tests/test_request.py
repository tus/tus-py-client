import base64
import hashlib

from parametrize import parametrize
import responses

from tusclient import request
from tests import mixin


FILEPATH_TEXT = "tests/sample_files/text.txt"
FILEPATH_BINARY = "tests/sample_files/binary.png"


class TusRequestTest(mixin.Mixin):
    def setUp(self):
        super(TusRequestTest, self).setUp()
        self.request = request.TusRequest(self.uploader)

    @parametrize(
        "filename",
        [FILEPATH_TEXT, FILEPATH_BINARY],
    )
    def test_perform(self, filename: str):
        with open(FILEPATH_TEXT, "rb") as stream, responses.RequestsMock() as resps:
            size = stream.tell()
            resps.add(responses.PATCH, self.url,
                      adding_headers={'upload-offset': str(size)},
                      status=204)

            self.request.perform()
            self.assertEqual(str(size), self.request.response_headers['upload-offset'])

    def test_perform_checksum(self):
        self.uploader.upload_checksum = True
        tus_request = request.TusRequest(self.uploader)

        with open(FILEPATH_TEXT, "rb") as stream, responses.RequestsMock() as resps:
            content = stream.read()
            expected_checksum = "sha1 " + \
                base64.standard_b64encode(hashlib.sha1(
                    content).digest()).decode("ascii")

            sent_checksum = ''
            def validate_headers(req):
                nonlocal sent_checksum
                sent_checksum = req.headers['upload-checksum']
                return (204, {}, None)

            resps.add_callback(responses.PATCH, self.url, callback=validate_headers)
            tus_request.perform()
            self.assertEqual(sent_checksum, expected_checksum)

    def test_verify_tls_cert(self):
        self.uploader.verify_tls_cert = False
        tus_request = request.TusRequest(self.uploader)

        with responses.RequestsMock() as resps:
            verify = None

            def validate_verify(req):
                nonlocal verify
                verify = req.req_kwargs['verify']
                return (204, {}, None)

            resps.add_callback(responses.PATCH, self.url, callback=validate_verify)
            tus_request.perform()
            self.assertEqual(verify, False)

