"""
Global Tusclient exception and warning classes.
"""


class TusCommunicationError(Exception):
    """
    Should be raised when communications with tus-server behaves
    unexpectedly.

    :Attributes:
        - message (str):
            Main message of the exception
        - status_code (int):
            Status code of response indicating an error
        - response_content (str):
            Content of response indicating an error
    :Constructor Args:
        - message (Optional[str])
        - status_code (Optional[int])
        - response_content (Optional[str])
    """

    def __init__(self, message, status_code=None, response_content=None):
        default_message = "Communication with tus server failed with status {}".format(
            status_code
        )
        message = message or default_message
        super(TusCommunicationError, self).__init__(message)
        self.status_code = status_code
        self.response_content = response_content


class TusDetailedError(TusCommunicationError):
    """Communication error that preserves original request and response context."""

    def __init__(
        self,
        message,
        status_code=None,
        response_content=None,
        causing_error=None,
        original_request_method=None,
        original_request_url=None,
        original_request_id=None,
        original_response_body=None,
        original_response_present=False,
        original_response_status=None,
    ):
        super(TusDetailedError, self).__init__(
            message,
            status_code=status_code,
            response_content=response_content,
        )
        self.causing_error = causing_error
        self.original_request_method = original_request_method
        self.original_request_url = original_request_url
        self.original_request_id = original_request_id
        self.original_response_body = original_response_body
        self.original_response_present = original_response_present
        self.original_response_status = original_response_status


class TusUploadFailed(TusCommunicationError):
    """Should be raised when an attempted upload fails"""
