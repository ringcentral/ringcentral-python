import json
import requests


class MultipartBuilder:
    def __init__(self):
        self._body = None
        self._contents = []
        self._boundary = ''
        pass

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
        return requests.Request(method, url, files=files)