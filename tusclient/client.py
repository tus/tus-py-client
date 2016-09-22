from tusclient import endpoint


class TusClient(object):
    DEFAULT_HEADER = {}

    def __init__(self, headers=None):
        if headers:
            self.headers = headers
        self.headers.update(self.DEFAULT_HEADERS)
        self.end_points = {}

    def set_headers(self, headers):
        self.headers.update(headers)

    def end_point(self, url):
        end_point = self.end_points.get(url)
        if not end_point:
            self.end_points[url] = endpoint.EndPoint(url)
        return self.end_points[url]
