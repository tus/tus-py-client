from typing import Dict, Optional, Tuple, Union

import requests

from tusclient.exceptions import TusCommunicationError
from tusclient.protocol_generated import (
    TERMINATE_UPLOAD_METHOD,
    is_successful_response_status,
    prepare_request_headers,
)
from tusclient.request_lifecycle import RequestLifecycleHooks
from tusclient.request_lifecycle import TusRequestContext
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

    def __init__(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        client_cert: Optional[Union[str, Tuple[str, str]]] = None,
        request_hooks: Optional[RequestLifecycleHooks] = None,
        add_request_id: bool = False,
    ):
        self.url = url
        self.headers = headers or {}
        self.client_cert = client_cert
        self.request_hooks = request_hooks
        self.add_request_id = add_request_id

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

    def set_request_hooks(self, request_hooks: Optional[RequestLifecycleHooks]):
        """
        Set callbacks that are invoked around each HTTP request/response pair.

        :Args:
            - request_hooks (Optional[RequestLifecycleHooks]):
                callbacks to invoke before transport send and after transport response.
        """
        self.request_hooks = request_hooks

    def enable_request_id_header(self):
        self.add_request_id = True

    def disable_request_id_header(self):
        self.add_request_id = False

    def terminate_upload(self, upload_url: str, verify_tls_cert: bool = True):
        headers = prepare_request_headers(None, self.headers, self.add_request_id)
        context = TusRequestContext(TERMINATE_UPLOAD_METHOD, upload_url, headers)
        if self.request_hooks is not None and self.request_hooks.before_request is not None:
            self.request_hooks.before_request(context)

        try:
            response = requests.request(
                TERMINATE_UPLOAD_METHOD,
                upload_url,
                headers=context.headers,
                verify=verify_tls_cert,
                cert=self.client_cert,
            )
        except requests.exceptions.RequestException as error:
            raise TusCommunicationError(error)

        if self.request_hooks is not None and self.request_hooks.after_response is not None:
            self.request_hooks.after_response(context, response)

        if not is_successful_response_status(response.status_code):
            raise TusCommunicationError(
                "unexpected status code ({}) while terminating upload".format(
                    response.status_code
                ),
                response.status_code,
                response.content,
            )

        return response

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

    def create_upload_with_data(self, bytes_to_upload: int, *args, **kwargs) -> Uploader:
        """
        Create an upload URL while sending the first bytes in the creation request.

        :Args:
            - bytes_to_upload (int):
                Number of bytes to send during upload creation.
            see tusclient.uploader.Uploader for remaining arguments.
        """
        uploader = self.uploader(*args, **kwargs)
        uploader.create_url_with_upload(bytes_to_upload)
        return uploader

    def async_uploader(self, *args, **kwargs) -> AsyncUploader:
        kwargs["client"] = self
        return AsyncUploader(*args, **kwargs)
