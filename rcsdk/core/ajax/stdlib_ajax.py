import httplib
from urlparse import urlparse
from .response import Response
from .ajax_exception import AjaxException

class Ajax:
    def __init__(self, request):
        self.__request = request
        self.__response = None

    def send(self):

        url = urlparse(self.__request.get_url())
        if url.scheme == "https":
            conn = httplib.HTTPSConnection(url.hostname, url.port)
        else:
            conn = httplib.HTTPConnection(url.hostname, url.port)
        try:
            conn.request(self.__request.get_method(),
                         self.__request.get_url(),
                         body=self.__request.get_encoded_body(),
                         headers=self.__request.get_headers())

            response = conn.getresponse()
            body = response.read()
            status_code = response.status
            headers = dict(response.getheaders())

            self.__response = Response(status_code, body, dict(headers))
            if not self.__response.check_status():
                raise AjaxException(self)

        finally:
            conn.close()

    def is_loaded(self):
        return True if self.__response else False

    def get_response(self):
        return self.__response

    def get_request(self):
        return self.__request