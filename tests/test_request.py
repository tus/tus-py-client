import base64
import io

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

    @parametrize(
        "algorithm,digest",
        [
            ("crc32", "cbf43926"),
            ("crc32c", "e3069283"),
            ("md5", "25f9e794323b453885f5181f1b624d0b"),
            ("sha1", "f7c3bc1d808e04732adf679965ccc34ca7ae3441"),
            (
                "sha256",
                "15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225",
            ),
            (
                "sha512",
                "d9e6762dd1c8eaf6d61b3c6192fc408d4d6d5f1176d0c29169bc24e71c3f274a"
                "d27fcd5811b313d681f7e55ec02d73d499c95455b6b5bb503acf574fba8ffe85",
            ),
        ],
    )
    def test_perform_checksum(self, algorithm: str, digest: str):
        content = b"123456789"
        expected_checksum = "{} {}".format(
            algorithm,
            base64.standard_b64encode(bytes.fromhex(digest)).decode("ascii"),
        )

        with responses.RequestsMock() as resps:
            resps.add(
                responses.HEAD,
                self.url,
                adding_headers={"upload-offset": "0"},
            )
            uploader = self.client.uploader(
                file_stream=io.BytesIO(content),
                url=self.url,
                upload_checksum=True,
                checksum_algorithm=algorithm,
            )
            tus_request = request.TusRequest(uploader)
            sent_checksum = ""

            def validate_headers(req):
                nonlocal sent_checksum
                sent_checksum = req.headers["upload-checksum"]
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
