"""
Global Tusclient exception and warning classes.
"""


class TusException(Exception):
    def __init__(self, message='', status_code=400, response_content=''):
        super(TusException, self).__init__(message)
        self.status_code = status_code
        self.response_content = response_content


class TusUploadFailed(TusException):
    """Should be raised when an attempted upload fails"""
    pass


class TusCommunicationError(TusException):
    """
    Should be raised when communications with tus-server behaves
    unexpectedly.
    """
    pass
