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
        default_message = 'Communication with tus server failed with status {}'.format(status_code)
        message = message or default_message
        super(TusCommunicationError, self).__init__(message)
        self.status_code = status_code
        self.response_content = response_content


class TusUploadFailed(TusCommunicationError):
    """Should be raised when an attempted upload fails"""
