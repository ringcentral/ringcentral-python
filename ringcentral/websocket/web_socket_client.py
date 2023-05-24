#!/usr/bin/env python
# encoding: utf-8
from observable import Observable
from websockets.sync.client import connect


class WebSocketClient(Observable):
    def __init__(self, platform):
        Observable.__init__(self)
        self._platform = platform
        self._web_socket = None

    def get_web_socket_token(self):
        try:
            response = self._platform.post("/restapi/oauth/wstoken", body={})
            return response.json_dict()
        except Exception as e:
            self.trigger("Get web socket token error", e)
            raise

    def open_connection(self, ws_uri, ws_access_token):
        try:
            with connect(f"{ws_uri}?access_token={ws_access_token}") as websocket:
                message = websocket.recv()
            connection_info = {}
            connection_info["connection"] = websocket
            connection_info["connection_details"] = message
            return connection_info
        except Exception as e:
            self.trigger("Open web socket connection error", e)
            raise

    def close_connection(self, ws_connection):
        try:
            ws_connection.close()
        except Exception as e:
            self.trigger("cClose web socket error", e)
            raise


if __name__ == "__main__":
    pass
