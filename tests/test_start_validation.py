from io import BytesIO

import pytest
import responses

from tusclient import client
from tusclient.start_validation import validate_upload_start


def test_start_validation_uses_generated_message_for_parallel_creation_upload():
    tus_client = client.TusClient("http://tusd.tusdemo.net/files/")

    validation = validate_upload_start(
        client=tus_client,
        file_stream=BytesIO(b"hello world"),
        parallel_uploads=2,
        upload_data_during_creation=True,
    )

    assert validation == {
        "message": "tus: cannot use the `uploadDataDuringCreation` option when parallelUploads is enabled",
        "ok": False,
        "reason": "parallelUploadsWithUploadDataDuringCreation",
    }


@responses.activate
def test_parallel_uploads_with_upload_url_fails_before_offset_request():
    tus_client = client.TusClient("http://tusd.tusdemo.net/files/")
    upload_url = "http://tusd.tusdemo.net/files/15acd89eabdf5738ffc"
    responses.add(responses.HEAD, upload_url, adding_headers={"upload-offset": "0"})

    with pytest.raises(ValueError) as error:
        tus_client.uploader(
            file_stream=BytesIO(b"hello world"),
            parallel_uploads=2,
            url=upload_url,
        )

    assert str(error.value) == (
        "tus: cannot use the `uploadUrl` option when parallelUploads is enabled"
    )
    assert len(responses.calls) == 0
