from typing import Optional, IO, Dict, TYPE_CHECKING
import os
import re
from base64 import b64encode
from sys import maxsize as MAXSIZE
import hashlib

import requests

from tusclient.exceptions import TusCommunicationError
from tusclient.request import TusRequest, catch_requests_error
from tusclient.fingerprint import fingerprint, interface
from tusclient.storage.interface import Storage

if TYPE_CHECKING:
    from tusclient.client import TusClient


class BaseUploader:
    """
    Object to control upload related functions.

    :Attributes:
        - file_path (str):
            This is the path(absolute/relative) to the file that is intended for upload
            to the tus server. On instantiation this attribute is required.
        - file_stream (file):
            As an alternative to the `file_path`, an instance of the file to be uploaded
            can be passed to the constructor as `file_stream`. Do note that either the
            `file_stream` or the `file_path` must be passed on instantiation.
        -  url (str):
            If the upload url for the file is known, it can be passed to the constructor.
            This may happen when you resume an upload.
        - client (<tusclient.client.TusClient>):
            An instance of `tusclient.client.TusClient`. This would tell the uploader instance
            what client it is operating with. Although this argument is optional, it is only
            optional if the 'url' argument is specified.
        - chunk_size (int):
            This tells the uploader what chunk size(in bytes) should be uploaded when the
            method `upload_chunk` is called. This defaults to the maximum possible integer if not
            specified.
        - metadata (dict):
            A dictionary containing the upload-metadata. This would be encoded internally
            by the method `encode_metadata` to conform with the tus protocol.
        - metadata_encoding (str):
            Encoding used for each upload-metadata value. This defaults to 'utf-8'.
        - offset (int):
            The offset value of the upload indicates the current position of the file upload.
        - stop_at (int):
            At what offset value the upload should stop.
        - request (<tusclient.request.TusRequest>):
            A http Request instance of the last chunk uploaded.
        - retries (int):
            The number of attempts the uploader should make in the case of a failed upload.
            If not specified, it defaults to 0.
        - retry_delay (int):
            How long (in seconds) the uploader should wait before retrying a failed upload attempt.
            If not specified, it defaults to 30.
        - verify_tls_cert (bool):
            Whether or not to verify the TLS certificate of the server.
            If not specified, it defaults to True.
        - store_url (bool):
            Determines whether or not url should be stored, and uploads should be resumed.
        - url_storage (<tusclient.storage.interface.Storage>):
            An implementation of <tusclient.storage.interface.Storage> which is an API for URL storage.
            This value must be set if store_url is set to true. A ready to use implementation exists atbe used out of the box. But you can
            implement your own custom storage API and pass an instace of it as value.
        - fingerprinter (<tusclient.fingerprint.interface.Fingerprint>):
            An implementation of <tusclient.fingerprint.interface.Fingerprint> which is an API to generate
            a unique fingerprint for the uploaded file. This is used for url storage when resumability is enabled.
            if store_url is set to true, the default fingerprint module (<tusclient.fingerprint.fingerprint.Fingerprint>)
            would be used. But you can set your own custom fingerprint module by passing it to the constructor.
        - upload_checksum (bool):
            Whether or not to supply the Upload-Checksum header along with each
            chunk. Defaults to False.

    :Constructor Args:
        - file_path (str)
        - file_stream (Optional[file])
        - url (Optional[str])
        - client (Optional [<tusclient.client.TusClient>])
        - chunk_size (Optional[int])
        - metadata (Optional[dict])
        - metadata_encoding (Optional[str])
        - retries (Optional[int])
        - retry_delay (Optional[int])
        - verify_tls_cert (Optional[bool])
        - store_url (Optional[bool])
        - url_storage (Optinal [<tusclient.storage.interface.Storage>])
        - fingerprinter (Optional [<tusclient.fingerprint.interface.Fingerprint>])
        - upload_checksum (Optional[bool])
    """
    DEFAULT_HEADERS = {"Tus-Resumable": "1.0.0"}
    DEFAULT_CHUNK_SIZE = MAXSIZE
    CHECKSUM_ALGORITHM_PAIR = ("sha1", hashlib.sha1, )

    def __init__(self, file_path: Optional[str] = None, file_stream: Optional[IO] = None,
                 url: Optional[str] = None, client: Optional['TusClient'] = None,
                 chunk_size: int = MAXSIZE, metadata: Optional[Dict] = None,
                 metadata_encoding: Optional[str] = 'utf-8',
                 retries: int = 0, retry_delay: int = 30,
                 verify_tls_cert: bool = True, store_url=False,
                 url_storage: Optional[Storage] = None,
                 fingerprinter: Optional[interface.Fingerprint] = None,
                 upload_checksum=False):
        if file_path is None and file_stream is None:
            raise ValueError(
                "Either 'file_path' or 'file_stream' cannot be None.")

        if url is None and client is None:
            raise ValueError("Either 'url' or 'client' cannot be None.")

        if store_url and url_storage is None:
            raise ValueError(
                "Please specify a storage instance to enable resumablility.")

        self.file_path = file_path
        self.file_stream = file_stream
        self.stop_at = self.get_file_size()
        self.client = client
        self.metadata = metadata or {}
        self.metadata_encoding = metadata_encoding
        self.store_url = store_url
        self.url_storage = url_storage
        self.fingerprinter = fingerprinter or fingerprint.Fingerprint()
        self.offset = 0
        self.url = None
        self.__init_url_and_offset(url)
        self.chunk_size = chunk_size
        self.verify_tls_cert = verify_tls_cert
        self.retries = retries
        self.request = None
        self._retried = 0
        self.retry_delay = retry_delay
        self.upload_checksum = upload_checksum
        self.__checksum_algorithm_name, self.__checksum_algorithm = \
            self.CHECKSUM_ALGORITHM_PAIR

    def get_headers(self):
        """
        Return headers of the uploader instance. This would include the headers of the
        client instance.
        """
        client_headers = getattr(self.client, 'headers', {})
        return dict(self.DEFAULT_HEADERS, **client_headers)

    def get_url_creation_headers(self):
        """Return headers required to create upload url"""
        headers = self.get_headers()
        headers['upload-length'] = str(self.get_file_size())
        headers['upload-metadata'] = ','.join(self.encode_metadata())
        return headers

    @property
    def checksum_algorithm(self):
        """The checksum algorithm to be used for the Upload-Checksum extension. 
        """
        return self.__checksum_algorithm

    @property
    def checksum_algorithm_name(self):
        """The name of the checksum algorithm to be used for the Upload-Checksum
        extension.
        """
        return self.__checksum_algorithm_name

    @catch_requests_error
    def get_offset(self):
        """
        Return offset from tus server.

        This is different from the instance attribute 'offset' because this makes an
        http request to the tus server to retrieve the offset.
        """
        resp = requests.head(self.url, headers=self.get_headers())
        offset = resp.headers.get('upload-offset')
        if offset is None:
            msg = 'Attempt to retrieve offset fails with status {}'.format(
                resp.status_code)
            raise TusCommunicationError(msg, resp.status_code, resp.content)
        return int(offset)

    def encode_metadata(self):
        """
        Return list of encoded metadata as defined by the Tus protocol.
        """
        encoded_list = []
        for key, value in self.metadata.items():
            key_str = str(key)  # dict keys may be of any object type.

            # confirm that the key does not contain unwanted characters.
            if re.search(r'^$|[\s,]+', key_str):
                msg = 'Upload-metadata key "{}" cannot be empty nor contain spaces or commas.'
                raise ValueError(msg.format(key_str))

            value_bytes = value.encode(self.metadata_encoding)
            encoded_list.append('{} {}'.format(
                key_str, b64encode(value_bytes).decode('ascii')))
        return encoded_list

    def __init_url_and_offset(self, url: Optional[str] = None):
        """
        Return the tus upload url.

        If resumability is enabled, this would try to get the url from storage if available,
        otherwise it would request a new upload url from the tus server.
        """
        if url:
            self.set_url(url)

        if self.store_url and self.url_storage:
            key = self._get_fingerprint()
            self.set_url(self.url_storage.get_item(key))

        if self.url:
            self.offset = self.get_offset()

    def _get_fingerprint(self):
        with self.get_file_stream() as stream:
            return self.fingerprinter.get_fingerprint(stream)

    def set_url(self, url: str):
        """Set the upload URL"""
        self.url = url
        if self.store_url and self.url_storage:
            key = self._get_fingerprint()
            self.url_storage.set_item(key, url)

    def get_request_length(self):
        """
        Return length of next chunk upload.
        """
        remainder = self.stop_at - self.offset
        return self.chunk_size if remainder > self.chunk_size else remainder

    def get_file_stream(self):
        """
        Return a file stream instance of the upload.
        """
        if self.file_stream:
            self.file_stream.seek(0)
            return self.file_stream
        elif os.path.isfile(self.file_path):
            return open(self.file_path, 'rb')
        else:
            raise ValueError("invalid file {}".format(self.file_path))

    def get_file_size(self):
        """
        Return size of the file.
        """
        stream = self.get_file_stream() 
        stream.seek(0, os.SEEK_END)
        return stream.tell()
