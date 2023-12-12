#!/usr/bin/env python
# encoding: utf-8
from observable import Observable
import websockets
from .web_socket_subscription import WebSocketSubscription
from .events import WebSocketEvents
import json
import asyncio
import uuid

class WebSocketClient(Observable):
    def __init__(self, platform):
        Observable.__init__(self)
        self._platform = platform
        self._web_socket = None
        self._done = False
        self._is_ready = False
        self._send_attempt_counter = 0

    async def create_new_connection(self):
        try:
            web_socket_token = self.get_web_socket_token()
            open_connection_response = await self.open_connection(
                web_socket_token["uri"], web_socket_token["ws_access_token"]
            )
            return open_connection_response
        except Exception as e:
            self.trigger(WebSocketEvents.createConnectionError, e)
            raise

    def get_web_socket_token(self):
        try:
            response = self._platform.post("/restapi/oauth/wstoken", body={})
            return response.json_dict()
        except Exception as e:
            self.trigger(WebSocketEvents.getTokenError, e)
            raise

    async def open_connection(self, ws_uri, ws_access_token):
        try:
            websocket = await websockets.connect(
                f"{ws_uri}?access_token={ws_access_token}"
            )
            connectionMessage = await websocket.recv()
            connection_info = {}
            connection_info["connection"] = websocket
            connection_info["connection_details"] = connectionMessage
            self._web_socket = connection_info
            self._is_ready = True
            self.trigger(WebSocketEvents.connectionCreated, self)

            # heartbeat every 10 minutes
            async def timer_function():
                while True:
                    if self._done:
                        timer.cancel()
                        break
                    await asyncio.sleep(600)
                    await self.send_message([{"type": "Heartbeat", "messageId": str(uuid.uuid4())}])
            timer = asyncio.create_task(timer_function())

            await asyncio.sleep(0)
            while True:
                message = await websocket.recv()
                self.trigger(WebSocketEvents.receiveMessage, message)
                await asyncio.sleep(0)
        except Exception as e:
            self.trigger(WebSocketEvents.createConnectionError, e)
            raise

    def get_connection_info(self):
        return self._web_socket

    def get_connection(self):
        return self._web_socket["connection"]

    async def close_connection(self):
        try:
            self._done = True
            self._is_ready = False
            ws_connection = self.get_connection()
            await ws_connection.close()
        except Exception as e:
            self.trigger(WebSocketEvents.closeConnectionError, e)
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
            self.trigger(WebSocketEvents.recoverConnectionError, e)
            raise

    async def send_message(self, message):
        try:
            if self._is_ready:
                self._send_attempt_counter = 0
                requestBodyJson = json.dumps(message)
                await self.get_connection().send(requestBodyJson)
            else:
                await asyncio.sleep(1)
                await self.send_message(message)
                self._send_attempt_counter += 1
                if(self._send_attempt_counter > 10):
                    self.trigger(WebSocketEvents.connectionNotReady)
                    self._send_attempt_counter = 0
                    raise
        except Exception as e:
            self.trigger(WebSocketEvents.sendMessageError, e)
            raise

    async def create_subscription(self, events=None):
        try:
            if self._is_ready:
                self._send_attempt_counter = 0
                subscription = WebSocketSubscription(self)
                await subscription.register(events)
            else:
                await asyncio.sleep(1)
                await self.create_subscription(events)
                self._send_attempt_counter += 1
                if(self._send_attempt_counter > 10):
                    self.trigger(WebSocketEvents.connectionNotReady)
                    self._send_attempt_counter = 0
                    raise
                
        except Exception as e:
            self.trigger(WebSocketEvents.createSubscriptionError, e)
            raise

    async def update_subscription(self, subscription, events=None):
        try:
            await subscription.update(events)
            return subscription
        except Exception as e:
            self.trigger(WebSocketEvents.updateSubscriptionError, e)
            raise

    async def remove_subscription(self, subscription):
        try:
            await subscription.remove()
        except Exception as e:
            self.trigger(WebSocketEvents.removeSubscriptionError, e)
            raise


if __name__ == "__main__":
    pass
