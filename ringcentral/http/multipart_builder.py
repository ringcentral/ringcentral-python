import json
import requests


class MultipartBuilder:
    def __init__(self, platform):
        self._body = None
        self._contents = []
        self._boundary = ''
        self._multipart_mixed = False
        self._platform = platform

    def set_multipart_mixed(self, multipart_mixed):
        self._multipart_mixed = multipart_mixed
        return self

    def set_body(self, body):
        self._body = body
        return self

    def body(self):
        return self._body

    def contents(self):
        return self._contents

    def add(self, attachment):
        """
        Possible attachment formats:

        1. Downloaded: ('filename.ext', urllib.urlopen('https://...').read(), 'image/png')
        2. Local file: ('report.xls', open('report.xls', 'rb'), 'application/vnd.ms-excel', {'Expires': '0'})
        3. Direct local file w/o meta: open('report.xls', 'rb')
        4. Plain text: ('report.csv', 'some,data,to,send')

        :param attachment:
        :return:
        """
        self._contents.append(('attachment', attachment))
        return self

    def request(self, url, method='POST'):
        files = [('json', ('request.json', json.dumps(self._body), 'application/json'))] + self._contents
        request = requests.Request(method, url, files=files)
        if self._multipart_mixed: # Ref: https://github.com/requests/requests/issues/1736#issuecomment-28470217
            request.url = self._platform.create_url(request.url, add_server=True) # prepare requires full url
            request = request.prepare()
            request.headers['Content-Type'] = request.headers['Content-Type'].replace('multipart/form-data;', 'multipart/mixed;')
        return request