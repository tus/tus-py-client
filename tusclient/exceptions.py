"""
Global Tusclient exception and warning classes.
"""


class TusUploadFailed(Exception):
    """Should be raised when an attempted upload fails"""
    pass


class TusCommunicationError(Exception):
    """
    Should be raised when communications with tus-server behaves
    unexpectedly.
    """
    pass
