import json
import unittest
import uuid

from observable import Observable

from .events import WebSocketEvents
from .web_socket_subscription import WebSocketSubscription


class RecordingHandler:
    def __init__(self):
        self.calls = []

    def __call__(self, *args):
        self.calls.append(args)


class FakeWebSocketClient(Observable):
    def __init__(self, responder=None, send_error=None):
        Observable.__init__(self)
        self.sent_messages = []
        self._responder = responder
        self._send_error = send_error

    async def send_message(self, message):
        self.sent_messages.append(message)
        if self._send_error is not None:
            raise self._send_error
        if self._responder is not None:
            response = self._responder(message)
            if response is not None:
                self.trigger(WebSocketEvents.receiveMessage, json.dumps(response))


def creation_response(request):
    return [
        {
            "type": "ClientRequest",
            "messageId": request[0]["messageId"],
            "status": 200,
            "headers": {
                "Server": "nginx",
                "Date": "Wed, 20 Aug 2025 22:23:55 GMT",
                "Content-Type": "application/json",
                "RoutingKey": "SJC01P07",
                "RCRequestId": "bedff5ae-9d68-4bc9-8653-7e34603ef562-2686696-1-19",
            },
        },
        {
            "uri": "/restapi/v1.0/subscription/1b2a2e6b-2245-4278-b47c-16259ca003a8",
            "id": "1b2a2e6b-2245-4278-b47c-16259ca003a8",
            "creationTime": "2025-08-20T22:23:55.169Z",
            "status": "Active",
            "eventFilters": ["/restapi/v1.0/account/809646016/extension/62264425016/presence"],
            "expirationTime": "2025-08-21T22:23:55.169Z",
            "expiresIn": 86399,
            "deliveryMode": {"transportType": "WebSocket", "encryption": False},
        },
    ]


EVENT_FILTERS = ["/restapi/v1.0/account/~/extension/~/presence"]


class WebSocketSubscriptionTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.web_socket_client = FakeWebSocketClient()

    async def test_successful_creation_before_send_returns_stores_response_and_emits_event_once(self):
        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        created = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionCreated, created)

        await subscription.subscribe(events=EVENT_FILTERS)

        self.assertEqual(len(created.calls), 1)
        self.assertIs(created.calls[0][0], subscription)
        self.assertEqual(len(self.web_socket_client.sent_messages), 1)
        stored = subscription.get_subscription_info()
        self.assertIsNotNone(stored)
        self.assertEqual(stored[0]["type"], "ClientRequest")
        self.assertEqual(
            stored[0]["messageId"], self.web_socket_client.sent_messages[0][0]["messageId"]
        )
        self.assertNotIn("WSG-SubscriptionId", stored[0]["headers"])
        self.assertEqual(
            stored[1]["id"], "1b2a2e6b-2245-4278-b47c-16259ca003a8"
        )

    async def test_unrelated_message_id_response_does_not_change_state_or_emit_events(self):
        def unrelated_response(request):
            response = creation_response(request)
            response[0]["messageId"] = "unrelated-" + request[0]["messageId"]
            return response

        self.web_socket_client._responder = unrelated_response
        subscription = WebSocketSubscription(self.web_socket_client)
        created = RecordingHandler()
        failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionCreated, created)
        self.web_socket_client.on(WebSocketEvents.createSubscriptionError, failed)

        await subscription.subscribe(events=EVENT_FILTERS)

        self.assertIsNone(subscription.get_subscription_info())
        self.assertEqual(created.calls, [])
        self.assertEqual(failed.calls, [])

    async def test_listener_remains_after_creation_so_notifications_are_emitted(self):
        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        created = RecordingHandler()
        notifications = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionCreated, created)
        self.web_socket_client.on(WebSocketEvents.receiveSubscriptionNotification, notifications)

        await subscription.subscribe(events=EVENT_FILTERS)
        self.assertEqual(len(created.calls), 1)

        server_notification = [
            {
                "type": "ServerNotification",
                "messageId": str(uuid.uuid4()),
                "headers": {"RoutingKey": "SJC01P07"},
            },
            {
                "uri": "/restapi/v1.0/subscription/1b2a2e6b-2245-4278-b47c-16259ca003a8",
                "event": {"/restapi/v1.0/account/~/extension/~/presence": {"activeCalls": []}},
            },
        ]
        self.web_socket_client.trigger(
            WebSocketEvents.receiveMessage, json.dumps(server_notification)
        )

        self.assertEqual(len(notifications.calls), 1)
        self.assertEqual(notifications.calls[0][0], server_notification)


if __name__ == "__main__":
    unittest.main()
