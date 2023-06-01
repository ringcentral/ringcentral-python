#!/usr/bin/env python
# encoding: utf-8
import uuid
import json
from observable import Observable

# _subscription format example: https://git.ringcentral.com/platform/wsg/-/blob/master/RingCentral_WebSocket_API.md#step-4-subscribing-to-rc-events


class WebSocketSubscription(Observable):
    def __init__(self, web_socket_connection):
        Observable.__init__(self)
        self._web_socket_connection = web_socket_connection
        self._event_filters = []
        self._subscription = None

    async def register(self, events=None):
        if not self._subscription:
            return await self.subscribe(events=events)
        else:
            return await self.update(events=events)

    def add_events(self, events):
        self._event_filters += events
        pass

    def set_events(self, events):
        self._event_filters = events

    async def subscribe(self, events=None):
        if events:
            self.set_events(events)

        if not self._event_filters or len(self._event_filters) == 0:
            raise Exception("Events are undefined")

        try:
            messageId = str(uuid.uuid4())
            requestBodyJson = json.dumps(
                [
                    {
                        "type": "ClientRequest",
                        "messageId": messageId,
                        "method": "POST",
                        "path": "/restapi/v1.0/subscription/",
                    },
                    {
                        "eventFilters": self._event_filters,
                        "deliveryMode": {"transportType": "WebSocket"},
                    },
                ]
            )
            await self._web_socket_connection.send(requestBodyJson)
            response = await self._web_socket_connection.recv()
            print("\n Subscription created: \n")
            print(response)

            self.set_subscription(json.loads(response))
            return response

        except Exception as e:
            self.reset()
            print(e)
            raise

    async def update(self, events=None):
        if events:
            self.set_events(events)

        if not self._event_filters or len(self._event_filters) == 0:
            raise Exception("Events are undefined")

        try:
            subscriptionId = self._subscription[1]["id"]
            messageId = str(uuid.uuid4())
            requestBodyJson = json.dumps(
                [
                    {
                        "type": "ClientRequest",
                        "messageId": messageId,
                        "method": "PUT",
                        "path": f"/restapi/v1.0/subscription/{subscriptionId}",
                    },
                    {
                        "eventFilters": self._event_filters,
                        "deliveryMode": {"transportType": "WebSocket"},
                    },
                ]
            )
            await self._web_socket_connection.send(requestBodyJson)
            response = await self._web_socket_connection.recv()
            print("\n Subscription updated: \n")
            print(response)

            self.set_subscription(json.loads(response))
            return response

        except Exception as e:
            self.reset()
            print(e)
            raise

    async def remove(self):
        subscriptionId = self._subscription[1]["id"]
        if not subscriptionId:
            raise Exception("Missing subscriptionId")

        try:
            messageId = str(uuid.uuid4())
            requestBodyJson = json.dumps(
                [
                    {
                        "type": "ClientRequest",
                        "messageId": messageId,
                        "method": "DELETE",
                        "path": f"/restapi/v1.0/subscription/{subscriptionId}",
                    }
                ]
            )

            await self._web_socket_connection.send(requestBodyJson)
            response = await self._web_socket_connection.recv()
            print("\n Subscription deleted: \n")
            print(response)

            self.reset()

            return response

        except Exception as e:
            self.reset()
            print(e)
            raise

    def set_subscription(self, data):
        self._subscription = data

    def get_subscription_info(self):
        return self._subscription

    def reset(self):
        self._subscription = None

    def destroy(self):
        self.reset()
        self.off()

if __name__ == "__main__":
    pass
