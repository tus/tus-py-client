from typing import Dict, Optional, Tuple, Union

from tusclient.uploader import Uploader, AsyncUploader


class TusClient:
    """
    Object representation of Tus client.

    :Attributes:
        - url (str):
            represents the tus server's create extension url. On instantiation this argument
            must be passed to the constructor.
        - headers (dict):
            This can be used to set the server specific headers. These headers would be sent
            along with every request made by the cleint to the server. This may be used to set
            authentication headers. These headers should not include headers required by tus
            protocol. If not set this defaults to an empty dictionary.
        - client_cert (str|tuple[str,str]):
            Path of PEM encoded client certitifacate and optionally path to PEM encoded
            key file. The PEM encoded key of the certificate can either be included in the
            certificate itself or be provided in a seperate file.
            Only unencrypted keys are supported!
    :Constructor Args:
        - url (str)
        - headers (Optiional[dict])
        - client_cert (Optional[str | Tuple[str, str]])
    """

    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None, client_cert: Optional[Union[str, Tuple[str, str]]] = None):
        self.url = url
        self.headers = headers or {}
        self.client_cert = client_cert

    def set_headers(self, headers: Dict[str, str]):
        """
        Set tus client headers.

        Update and/or set new headers that would be sent along with every request made
        to the server.

        :Args:
            - headers (dict):
                key, value pairs of the headers to be set. This argument is required.
        """
        self.headers.update(headers)

    def uploader(self, *args, **kwargs) -> Uploader:
        """
        Return uploader instance pointing at current client instance.

        Return uploader instance with which you can control the upload of a specific
        file. The current instance of the tus client is passed to the uploader on creation.

        :Args:
            see tusclient.uploader.Uploader for required and optional arguments.
        """
        kwargs["client"] = self
        return Uploader(*args, **kwargs)

    def async_uploader(self, *args, **kwargs) -> AsyncUploader:
        kwargs["client"] = self
        return AsyncUploader(*args, **kwargs)
