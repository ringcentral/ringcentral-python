#!/usr/bin/env python
# encoding: utf-8
import uuid
import json
from .events import WebSocketEvents
from observable import Observable

# _subscription format example: https://git.ringcentral.com/platform/wsg/-/blob/master/RingCentral_WebSocket_API.md#step-4-subscribing-to-rc-events


class WebSocketSubscription(Observable):
    def __init__(self, web_socket_client):
        Observable.__init__(self)
        self._web_socket_client = web_socket_client
        self._event_filters = []
        self._subscription = None
        self._pending_creation_message_id = None
        self._pending_update_message_id = None
        self._pending_update_filters = None
        self._pending_removal_message_id = None
        self._receive_message_listener_attached = False

    def _operation_pending(self):
        return (
            self._pending_creation_message_id is not None
            or self._pending_update_message_id is not None
            or self._pending_removal_message_id is not None
        )

    def on_message(self, message):
        message_json = json.loads(message)
        if(
            self._pending_creation_message_id is not None
            and message_json[0].get('type') == 'ClientRequest'
            and message_json[0].get('messageId') == self._pending_creation_message_id
        ):
            status = message_json[0].get('status', 0)
            self._pending_creation_message_id = None
            if 200 <= status < 300:
                self.set_subscription(message_json)
                self._web_socket_client.trigger(WebSocketEvents.subscriptionCreated, self)
            else:
                error = Exception(f"WebSocket subscription creation failed with status {status}")
                self._web_socket_client.trigger(WebSocketEvents.createSubscriptionError, error)
        elif(
            self._pending_update_message_id is not None
            and message_json[0].get('messageId') == self._pending_update_message_id
        ):
            status = message_json[0].get('status', 0)
            proposed_filters = self._pending_update_filters
            self._pending_update_message_id = None
            self._pending_update_filters = None
            if 200 <= status < 300:
                self.set_subscription(message_json)
                self.set_events(proposed_filters)
                self._web_socket_client.trigger(WebSocketEvents.subscriptionUpdated, self)
            else:
                error = Exception(f"WebSocket subscription update failed with status {status}")
                self._web_socket_client.trigger(WebSocketEvents.updateSubscriptionError, error)
        elif(
            self._pending_removal_message_id is not None
            and message_json[0].get('messageId') == self._pending_removal_message_id
        ):
            status = message_json[0].get('status', 0)
            self._pending_removal_message_id = None
            if 200 <= status < 300:
                if self._receive_message_listener_attached:
                    self._web_socket_client.off(WebSocketEvents.receiveMessage, self.on_message)
                    self._receive_message_listener_attached = False
                self.reset()
                self._web_socket_client.trigger(WebSocketEvents.subscriptionRemoved)
            else:
                error = Exception(f"WebSocket subscription removal failed with status {status}")
                self._web_socket_client.trigger(WebSocketEvents.removeSubscriptionError, error)
        elif message_json[0].get('type') == 'ServerNotification':
            self._web_socket_client.trigger(WebSocketEvents.receiveSubscriptionNotification, message_json)

    async def register(self, events=None):
        if not self._subscription:
            await self.subscribe(events=events)
        else:
            await self.update(events=events)

    def add_events(self, events):
        self._event_filters += events
        pass

    def set_events(self, events):
        self._event_filters = events

    async def subscribe(self, events=None):
        if self._pending_creation_message_id is not None:
            raise Exception("Subscription creation is already in progress")

        if events:
            self.set_events(events)

        if not self._event_filters or len(self._event_filters) == 0:
            raise Exception("Events are undefined")

        newly_attached = False
        try:
            messageId = str(uuid.uuid4())
            self._pending_creation_message_id = messageId
            requestBodyJson = [
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
            if not self._receive_message_listener_attached:
                self._web_socket_client.on(WebSocketEvents.receiveMessage, self.on_message)
                self._receive_message_listener_attached = True
                newly_attached = True
            await self._web_socket_client.send_message(requestBodyJson)

        except Exception as e:
            self._pending_creation_message_id = None
            if newly_attached:
                self._web_socket_client.off(WebSocketEvents.receiveMessage, self.on_message)
                self._receive_message_listener_attached = False
            self.reset()
            print(e)
            raise

    async def update(self, events=None):
        if self._operation_pending():
            raise Exception("Subscription update is already in progress")

        proposed_filters = events if events else self._event_filters
        if not proposed_filters or len(proposed_filters) == 0:
            raise Exception("Events are undefined")

        try:
            subscriptionId = self._subscription[1]["id"]
            messageId = str(uuid.uuid4())
            self._pending_update_message_id = messageId
            self._pending_update_filters = proposed_filters
            requestBodyJson = [
                {
                    "type": "ClientRequest",
                    "messageId": messageId,
                    "method": "PUT",
                    "path": f"/restapi/v1.0/subscription/{subscriptionId}",
                },
                {
                    "eventFilters": proposed_filters,
                    "deliveryMode": {"transportType": "WebSocket"},
                },
            ]
            await self._web_socket_client.send_message(requestBodyJson)

        except Exception as e:
            self._pending_update_message_id = None
            self._pending_update_filters = None
            print(e)
            raise

    async def remove(self):
        if self._operation_pending():
            raise Exception("Subscription removal is already in progress")

        subscriptionId = self._subscription[1]["id"]
        if not subscriptionId:
            raise Exception("Missing subscriptionId")

        try:
            messageId = str(uuid.uuid4())
            self._pending_removal_message_id = messageId
            requestBodyJson = [
                {
                    "type": "ClientRequest",
                    "messageId": messageId,
                    "method": "DELETE",
                    "path": f"/restapi/v1.0/subscription/{subscriptionId}",
                }
            ]

            await self._web_socket_client.send_message(requestBodyJson)

        except Exception as e:
            self._pending_removal_message_id = None
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
