#!/usr/bin/env python
# encoding: utf-8
from observable import Observable
import websockets
from .web_socket_subscription import WebSocketSubscription


class WebSocketClient(Observable):
    def __init__(self, platform):
        Observable.__init__(self)
        self._platform = platform
        self._web_socket = None
        self._done = False

    async def create_new_connection(self):
        try:
            web_socket_token = self.get_web_socket_token()
            open_connection_response = await self.open_connection(
                web_socket_token["uri"], web_socket_token["ws_access_token"]
            )
            return open_connection_response
        except Exception as e:
            self.trigger("Create new WebSocket connection error", e)
            raise

    def get_web_socket_token(self):
        try:
            response = self._platform.post("/restapi/oauth/wstoken", body={})
            return response.json_dict()
        except Exception as e:
            self.trigger("Get WebSocket token error", e)
            raise

    async def open_connection(self, ws_uri, ws_access_token):
        try:
            websocket = await websockets.connect(f"{ws_uri}?access_token={ws_access_token}")
            connectionMessage = await websocket.recv()
            connection_info = {}
            connection_info["connection"] = websocket
            connection_info["connection_details"] = connectionMessage
            self._web_socket = connection_info
            return connection_info
        except Exception as e:
            self.trigger("Open WebSocket connection error", e)
            raise

    def get_connection_info(self):
        return self._web_socket

    def get_connection(self):
        return self._web_socket["connection"]

    async def close_connection(self):
        try:
            self._done = True
            ws_connection = self.get_connection()
            await ws_connection.close()
        except Exception as e:
            self.trigger("Close WebSocket error", e)
            raise

    async def recover_connection(self):
        try:
            ws_connection_info = self.get_web_socket_token()
            recovered_connection_info = await self.open_connection(
                ws_connection_info["uri"], ws_connection_info["ws_access_token"]
            )
            # if recovered_connection_info['recoveryState'] === "Successful", then subscription is restored
            # otherwise, need to create a new subscription
            # IMPORTANT: WebSocket creation is successful if it doesn't raise any exception
            return recovered_connection_info
        except Exception as e:
            self.trigger("Recover WebSocket error", e)
            raise

    async def create_subscription(self, events=None):
        try:
            subscription = WebSocketSubscription(self.get_connection())
            await subscription.register(events)
            return subscription
        except Exception as e:
            self.trigger("Create subscription error", e)
            raise

    async def update_subscription(self, subscription, events=None):
        try:
            await subscription.update(events)
            return subscription
        except Exception as e:
            self.trigger("Update subscription error", e)
            raise

    async def remove_subscription(self, subscription):
        try:
            await subscription.remove()
        except Exception as e:
            self.trigger("Remove subscription error", e)
            raise


if __name__ == "__main__":
    pass
