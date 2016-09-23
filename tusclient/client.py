from tusclient import endpoint


class TusClient(object):

    def __init__(self, headers=None):
        if headers is None:
            headers = {}

        self.headers = headers
        self.end_points = {}

    # you can set authentication headers with this.
    def set_headers(self, headers):
        self.headers.update(headers)

    def end_point(self, url):
        end_point = self.end_points.get(url)
        if not end_point:
            self.end_points[url] = endpoint.EndPoint(url)
        return self.end_points[url]
