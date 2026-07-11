class TusRequestContext:
    """Request context passed to lifecycle hooks before transport sends."""

    def __init__(self, method, url, headers):
        self.method = method
        self.url = url
        self.headers = headers


class RequestLifecycleHooks:
    """Callbacks invoked around each HTTP request/response pair."""

    def __init__(self, before_request=None, after_response=None):
        self.before_request = before_request
        self.after_response = after_response
