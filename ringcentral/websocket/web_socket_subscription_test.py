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
        self.receive_message_listener_count = 0
        self._responder = responder
        self._send_error = send_error

    def on(self, event, *handlers):
        if event == WebSocketEvents.receiveMessage:
            self.receive_message_listener_count += len(handlers)
        return Observable.on(self, event, *handlers)

    def off(self, event=None, *handlers):
        if event == WebSocketEvents.receiveMessage:
            self.receive_message_listener_count -= len(handlers)
        return Observable.off(self, event, *handlers)

    async def send_message(self, message):
        self.sent_messages.append(message)
        if self._send_error is not None:
            error = self._send_error
            self._send_error = None
            raise error
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


def rejected_creation_response(request, status=403):
    response = creation_response(request)
    response[0]["status"] = status
    return response


def update_response(request, status=200, message_type="ClientRequest"):
    return [
        {
            "type": message_type,
            "messageId": request[0]["messageId"],
            "status": status,
            "headers": {
                "Server": "nginx",
                "Date": "Wed, 20 Aug 2025 22:23:55 GMT",
                "Content-Type": "application/json",
                "RoutingKey": "SJC01P07",
                "RCRequestId": "bedff5ae-9d68-4bc9-8653-7e34603ef562-2686696-1-19",
            },
        },
        {
            "uri": "/restapi/v1.0/subscription/9d3b7f10-5c11-4b6e-8a2f-6f8b56f0f1c2",
            "id": "9d3b7f10-5c11-4b6e-8a2f-6f8b56f0f1c2",
            "creationTime": "2025-08-20T22:23:55.169Z",
            "status": "Active",
            "eventFilters": request[1]["eventFilters"],
            "expirationTime": "2025-08-21T22:23:55.169Z",
            "expiresIn": 86399,
            "deliveryMode": {"transportType": "WebSocket", "encryption": False},
        },
    ]


def removal_response(request, status=200, message_type="ClientRequest"):
    return [
        {
            "type": message_type,
            "messageId": request[0]["messageId"],
            "status": status,
            "headers": {
                "Server": "nginx",
                "Date": "Wed, 20 Aug 2025 22:23:55 GMT",
                "RCRequestId": "bedff5ae-9d68-4bc9-8653-7e34603ef562-2686696-1-19",
            },
        }
    ]


EVENT_FILTERS = ["/restapi/v1.0/account/~/extension/~/presence"]
OTHER_FILTERS = ["/restapi/v1.0/account/~/extension/~/message-store"]


def server_notification():
    return [
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

        notification = server_notification()
        self.web_socket_client.trigger(WebSocketEvents.receiveMessage, json.dumps(notification))

        self.assertEqual(len(notifications.calls), 1)
        self.assertEqual(notifications.calls[0][0], notification)

    async def test_rejected_creation_emits_single_error_without_state_or_success(self):
        self.web_socket_client._responder = rejected_creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        created = RecordingHandler()
        failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionCreated, created)
        self.web_socket_client.on(WebSocketEvents.createSubscriptionError, failed)

        await subscription.subscribe(events=EVENT_FILTERS)

        self.assertEqual(len(failed.calls), 1)
        error = failed.calls[0][0]
        self.assertIsInstance(error, Exception)
        self.assertEqual(
            str(error), "WebSocket subscription creation failed with status 403"
        )
        self.assertEqual(created.calls, [])
        self.assertIsNone(subscription.get_subscription_info())

    async def test_retry_after_rejected_creation_sends_new_request_and_can_succeed(self):
        self.web_socket_client._responder = rejected_creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        created = RecordingHandler()
        failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionCreated, created)
        self.web_socket_client.on(WebSocketEvents.createSubscriptionError, failed)

        await subscription.subscribe(events=EVENT_FILTERS)
        self.assertEqual(len(failed.calls), 1)

        self.web_socket_client._responder = creation_response
        await subscription.subscribe(events=EVENT_FILTERS)

        self.assertEqual(len(self.web_socket_client.sent_messages), 2)
        self.assertEqual(len(failed.calls), 1)
        self.assertEqual(len(created.calls), 1)
        self.assertIsNotNone(subscription.get_subscription_info())

    async def test_second_creation_while_pending_is_rejected_without_new_request_or_listener(self):
        self.web_socket_client._responder = None
        subscription = WebSocketSubscription(self.web_socket_client)
        created = RecordingHandler()
        failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionCreated, created)
        self.web_socket_client.on(WebSocketEvents.createSubscriptionError, failed)

        await subscription.subscribe(events=EVENT_FILTERS)
        self.assertEqual(len(self.web_socket_client.sent_messages), 1)
        listeners_before = self.web_socket_client.receive_message_listener_count

        with self.assertRaises(Exception):
            await subscription.subscribe(events=EVENT_FILTERS)

        self.assertEqual(len(self.web_socket_client.sent_messages), 1)
        self.assertEqual(
            self.web_socket_client.receive_message_listener_count, listeners_before
        )

        self.web_socket_client._responder = creation_response
        pending_request = self.web_socket_client.sent_messages[0]
        self.web_socket_client.trigger(
            WebSocketEvents.receiveMessage, json.dumps(creation_response(pending_request))
        )

        self.assertEqual(len(created.calls), 1)
        self.assertEqual(failed.calls, [])
        self.assertIsNotNone(subscription.get_subscription_info())

    async def test_second_creation_while_pending_leaves_original_filters_for_update(self):
        self.web_socket_client._responder = None
        subscription = WebSocketSubscription(self.web_socket_client)
        created = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionCreated, created)

        await subscription.subscribe(events=EVENT_FILTERS)
        self.assertEqual(len(self.web_socket_client.sent_messages), 1)

        with self.assertRaises(Exception):
            await subscription.subscribe(events=OTHER_FILTERS)

        pending_request = self.web_socket_client.sent_messages[0]
        self.web_socket_client._responder = creation_response
        self.web_socket_client.trigger(
            WebSocketEvents.receiveMessage, json.dumps(creation_response(pending_request))
        )
        self.assertEqual(len(created.calls), 1)

        await subscription.update()

        self.assertEqual(len(self.web_socket_client.sent_messages), 2)
        self.assertEqual(
            self.web_socket_client.sent_messages[1][1]["eventFilters"], EVENT_FILTERS
        )

    async def test_failed_send_clears_pending_and_new_listener_and_retry_succeeds(self):
        self.web_socket_client._responder = creation_response
        self.web_socket_client._send_error = Exception("connection closed")
        subscription = WebSocketSubscription(self.web_socket_client)
        created = RecordingHandler()
        notifications = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionCreated, created)
        self.web_socket_client.on(WebSocketEvents.receiveSubscriptionNotification, notifications)

        with self.assertRaises(Exception):
            await subscription.subscribe(events=EVENT_FILTERS)

        self.assertEqual(len(self.web_socket_client.sent_messages), 1)
        self.assertIsNone(subscription.get_subscription_info())
        self.assertEqual(created.calls, [])
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 0)

        await subscription.subscribe(events=EVENT_FILTERS)

        self.assertEqual(len(self.web_socket_client.sent_messages), 2)
        self.assertEqual(len(created.calls), 1)
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 1)

        notification = server_notification()
        self.web_socket_client.trigger(WebSocketEvents.receiveMessage, json.dumps(notification))
        self.assertEqual(len(notifications.calls), 1)

    async def test_removal_detaches_listener_and_later_retry_receives_notifications_once(self):
        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        notifications = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.receiveSubscriptionNotification, notifications)

        await subscription.subscribe(events=EVENT_FILTERS)
        notification = server_notification()
        self.web_socket_client.trigger(WebSocketEvents.receiveMessage, json.dumps(notification))
        self.assertEqual(len(notifications.calls), 1)

        await subscription.remove()
        self.web_socket_client.trigger(WebSocketEvents.receiveMessage, json.dumps(server_notification()))
        self.assertEqual(len(notifications.calls), 1)
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 0)

        await subscription.subscribe(events=EVENT_FILTERS)
        self.web_socket_client.trigger(WebSocketEvents.receiveMessage, json.dumps(server_notification()))
        self.assertEqual(len(notifications.calls), 2)
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 1)

    async def test_update_send_without_response_emits_nothing_and_preserves_confirmed_state(self):
        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        await subscription.subscribe(events=EVENT_FILTERS)
        confirmed = subscription.get_subscription_info()

        updated = RecordingHandler()
        failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionUpdated, updated)
        self.web_socket_client.on(WebSocketEvents.updateSubscriptionError, failed)

        self.web_socket_client._responder = None
        await subscription.update(events=OTHER_FILTERS)

        self.assertEqual(len(self.web_socket_client.sent_messages), 2)
        self.assertEqual(self.web_socket_client.sent_messages[1][0]["method"], "PUT")
        self.assertEqual(self.web_socket_client.sent_messages[1][1]["eventFilters"], OTHER_FILTERS)
        self.assertEqual(updated.calls, [])
        self.assertEqual(failed.calls, [])
        self.assertIs(subscription.get_subscription_info(), confirmed)
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 1)

    async def test_confirmed_update_response_commits_envelope_and_filters_before_single_event(self):
        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        await subscription.subscribe(events=EVENT_FILTERS)

        observed_at_event = []

        def on_updated(updated_subscription):
            observed_at_event.append(updated_subscription.get_subscription_info())

        updated = RecordingHandler()
        failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionUpdated, on_updated)
        self.web_socket_client.on(WebSocketEvents.subscriptionUpdated, updated)
        self.web_socket_client.on(WebSocketEvents.updateSubscriptionError, failed)

        self.web_socket_client._responder = update_response
        await subscription.update(events=OTHER_FILTERS)

        self.assertEqual(len(updated.calls), 1)
        self.assertIs(updated.calls[0][0], subscription)
        self.assertEqual(failed.calls, [])
        stored = subscription.get_subscription_info()
        self.assertEqual(
            stored[0]["messageId"], self.web_socket_client.sent_messages[1][0]["messageId"]
        )
        self.assertEqual(stored[1]["id"], "9d3b7f10-5c11-4b6e-8a2f-6f8b56f0f1c2")
        self.assertEqual(stored[1]["eventFilters"], OTHER_FILTERS)
        self.assertEqual(observed_at_event, [stored])

        self.web_socket_client._responder = None
        await subscription.update()
        self.assertEqual(self.web_socket_client.sent_messages[2][1]["eventFilters"], OTHER_FILTERS)

    async def test_rejected_update_response_emits_single_error_preserves_state_and_permits_retry(self):
        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        await subscription.subscribe(events=EVENT_FILTERS)
        confirmed = subscription.get_subscription_info()

        updated = RecordingHandler()
        failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionUpdated, updated)
        self.web_socket_client.on(WebSocketEvents.updateSubscriptionError, failed)

        self.web_socket_client._responder = lambda request: update_response(request, status=404)
        await subscription.update(events=OTHER_FILTERS)

        self.assertEqual(len(failed.calls), 1)
        error = failed.calls[0][0]
        self.assertIsInstance(error, Exception)
        self.assertEqual(
            str(error), "WebSocket subscription update failed with status 404"
        )
        self.assertEqual(updated.calls, [])
        self.assertIs(subscription.get_subscription_info(), confirmed)

        self.web_socket_client._responder = update_response
        await subscription.update()

        self.assertEqual(len(updated.calls), 1)
        self.assertEqual(self.web_socket_client.sent_messages[2][1]["eventFilters"], EVENT_FILTERS)

    async def test_unrelated_update_response_is_ignored_and_pending_update_still_completes(self):
        def unrelated_update_response(request):
            response = update_response(request)
            response[0]["messageId"] = "unrelated-" + request[0]["messageId"]
            return response

        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        await subscription.subscribe(events=EVENT_FILTERS)
        confirmed = subscription.get_subscription_info()

        updated = RecordingHandler()
        failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionUpdated, updated)
        self.web_socket_client.on(WebSocketEvents.updateSubscriptionError, failed)

        self.web_socket_client._responder = unrelated_update_response
        await subscription.update(events=OTHER_FILTERS)

        self.assertEqual(updated.calls, [])
        self.assertEqual(failed.calls, [])
        self.assertIs(subscription.get_subscription_info(), confirmed)

        pending_request = self.web_socket_client.sent_messages[1]
        self.web_socket_client.trigger(
            WebSocketEvents.receiveMessage, json.dumps(update_response(pending_request))
        )

        self.assertEqual(len(updated.calls), 1)
        self.assertEqual(failed.calls, [])
        self.assertEqual(
            subscription.get_subscription_info()[0]["messageId"], pending_request[0]["messageId"]
        )

    async def test_update_send_failure_preserves_state_and_permits_retry_after_late_response(self):
        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        await subscription.subscribe(events=EVENT_FILTERS)
        confirmed = subscription.get_subscription_info()

        updated = RecordingHandler()
        failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionUpdated, updated)
        self.web_socket_client.on(WebSocketEvents.updateSubscriptionError, failed)

        self.web_socket_client._send_error = Exception("connection closed")
        with self.assertRaises(Exception):
            await subscription.update(events=OTHER_FILTERS)

        self.assertEqual(updated.calls, [])
        self.assertEqual(failed.calls, [])
        self.assertIs(subscription.get_subscription_info(), confirmed)

        pending_request = self.web_socket_client.sent_messages[1]
        self.web_socket_client.trigger(
            WebSocketEvents.receiveMessage, json.dumps(update_response(pending_request))
        )
        self.assertEqual(updated.calls, [])
        self.assertEqual(failed.calls, [])
        self.assertIs(subscription.get_subscription_info(), confirmed)

        self.web_socket_client._responder = update_response
        await subscription.update()

        self.assertEqual(len(updated.calls), 1)
        self.assertEqual(self.web_socket_client.sent_messages[2][1]["eventFilters"], EVENT_FILTERS)

    async def test_overlapping_update_and_removal_while_update_pending_are_rejected_without_side_effects(self):
        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        await subscription.subscribe(events=EVENT_FILTERS)
        confirmed = subscription.get_subscription_info()

        updated = RecordingHandler()
        removed = RecordingHandler()
        failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionUpdated, updated)
        self.web_socket_client.on(WebSocketEvents.subscriptionRemoved, removed)
        self.web_socket_client.on(WebSocketEvents.updateSubscriptionError, failed)

        self.web_socket_client._responder = None
        await subscription.update(events=OTHER_FILTERS)
        self.assertEqual(len(self.web_socket_client.sent_messages), 2)

        with self.assertRaises(Exception):
            await subscription.update(events=OTHER_FILTERS)
        with self.assertRaises(Exception):
            await subscription.remove()

        self.assertEqual(len(self.web_socket_client.sent_messages), 2)
        self.assertIs(subscription.get_subscription_info(), confirmed)
        self.assertEqual(updated.calls, [])
        self.assertEqual(removed.calls, [])

        pending_request = self.web_socket_client.sent_messages[1]
        self.web_socket_client.trigger(
            WebSocketEvents.receiveMessage, json.dumps(update_response(pending_request, status=403))
        )
        self.assertEqual(len(failed.calls), 1)
        self.assertEqual(updated.calls, [])
        self.assertIs(subscription.get_subscription_info(), confirmed)

        self.web_socket_client._responder = update_response
        await subscription.update()

        self.assertEqual(len(self.web_socket_client.sent_messages), 3)
        self.assertEqual(self.web_socket_client.sent_messages[2][1]["eventFilters"], EVENT_FILTERS)

    async def test_removal_send_without_response_preserves_state_listener_and_emits_nothing(self):
        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        await subscription.subscribe(events=EVENT_FILTERS)
        confirmed = subscription.get_subscription_info()

        removed = RecordingHandler()
        failed = RecordingHandler()
        notifications = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionRemoved, removed)
        self.web_socket_client.on(WebSocketEvents.removeSubscriptionError, failed)
        self.web_socket_client.on(WebSocketEvents.receiveSubscriptionNotification, notifications)

        self.web_socket_client._responder = None
        await subscription.remove()

        self.assertEqual(len(self.web_socket_client.sent_messages), 2)
        self.assertEqual(self.web_socket_client.sent_messages[1][0]["method"], "DELETE")
        self.assertEqual(removed.calls, [])
        self.assertEqual(failed.calls, [])
        self.assertIs(subscription.get_subscription_info(), confirmed)
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 1)

        self.web_socket_client.trigger(WebSocketEvents.receiveMessage, json.dumps(server_notification()))
        self.assertEqual(len(notifications.calls), 1)

    async def test_confirmed_removal_clears_state_and_detaches_listener_before_single_event(self):
        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        await subscription.subscribe(events=EVENT_FILTERS)
        notifications = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.receiveSubscriptionNotification, notifications)

        observed_at_event = []

        def on_removed(*args):
            observed_at_event.append(
                (
                    args,
                    subscription.get_subscription_info(),
                    self.web_socket_client.receive_message_listener_count,
                )
            )

        removed = RecordingHandler()
        failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionRemoved, on_removed)
        self.web_socket_client.on(WebSocketEvents.subscriptionRemoved, removed)
        self.web_socket_client.on(WebSocketEvents.removeSubscriptionError, failed)

        self.web_socket_client._responder = removal_response
        await subscription.remove()

        self.assertEqual(len(removed.calls), 1)
        self.assertEqual(removed.calls[0], ())
        self.assertEqual(failed.calls, [])
        self.assertEqual(observed_at_event, [((), None, 0)])
        self.assertIsNone(subscription.get_subscription_info())
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 0)

        self.web_socket_client.trigger(WebSocketEvents.receiveMessage, json.dumps(server_notification()))
        self.assertEqual(len(notifications.calls), 0)

    async def test_rejected_removal_response_emits_single_error_and_preserves_everything(self):
        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        await subscription.subscribe(events=EVENT_FILTERS)
        confirmed = subscription.get_subscription_info()
        notifications = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.receiveSubscriptionNotification, notifications)

        removed = RecordingHandler()
        failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionRemoved, removed)
        self.web_socket_client.on(WebSocketEvents.removeSubscriptionError, failed)

        self.web_socket_client._responder = lambda request: removal_response(request, status=404)
        await subscription.remove()

        self.assertEqual(len(failed.calls), 1)
        error = failed.calls[0][0]
        self.assertIsInstance(error, Exception)
        self.assertEqual(
            str(error), "WebSocket subscription removal failed with status 404"
        )
        self.assertEqual(removed.calls, [])
        self.assertIs(subscription.get_subscription_info(), confirmed)
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 1)

        self.web_socket_client.trigger(WebSocketEvents.receiveMessage, json.dumps(server_notification()))
        self.assertEqual(len(notifications.calls), 1)

        self.web_socket_client._responder = removal_response
        await subscription.remove()

        self.assertEqual(len(removed.calls), 1)
        self.assertIsNone(subscription.get_subscription_info())
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 0)

    async def test_unrelated_removal_response_is_ignored_and_pending_removal_still_completes(self):
        def unrelated_removal_response(request):
            response = removal_response(request)
            response[0]["messageId"] = "unrelated-" + request[0]["messageId"]
            return response

        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        await subscription.subscribe(events=EVENT_FILTERS)
        confirmed = subscription.get_subscription_info()

        removed = RecordingHandler()
        failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionRemoved, removed)
        self.web_socket_client.on(WebSocketEvents.removeSubscriptionError, failed)

        self.web_socket_client._responder = unrelated_removal_response
        await subscription.remove()

        self.assertEqual(removed.calls, [])
        self.assertEqual(failed.calls, [])
        self.assertIs(subscription.get_subscription_info(), confirmed)
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 1)

        pending_request = self.web_socket_client.sent_messages[1]
        self.web_socket_client.trigger(
            WebSocketEvents.receiveMessage, json.dumps(removal_response(pending_request))
        )

        self.assertEqual(len(removed.calls), 1)
        self.assertEqual(failed.calls, [])
        self.assertIsNone(subscription.get_subscription_info())
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 0)

    async def test_removal_send_failure_preserves_state_and_listener_and_permits_retry(self):
        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        await subscription.subscribe(events=EVENT_FILTERS)
        confirmed = subscription.get_subscription_info()

        removed = RecordingHandler()
        failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionRemoved, removed)
        self.web_socket_client.on(WebSocketEvents.removeSubscriptionError, failed)

        self.web_socket_client._send_error = Exception("connection closed")
        with self.assertRaises(Exception):
            await subscription.remove()

        self.assertEqual(removed.calls, [])
        self.assertEqual(failed.calls, [])
        self.assertIs(subscription.get_subscription_info(), confirmed)
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 1)

        pending_request = self.web_socket_client.sent_messages[1]
        self.web_socket_client.trigger(
            WebSocketEvents.receiveMessage, json.dumps(removal_response(pending_request))
        )
        self.assertEqual(removed.calls, [])
        self.assertEqual(failed.calls, [])
        self.assertIs(subscription.get_subscription_info(), confirmed)
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 1)

        self.web_socket_client._responder = removal_response
        await subscription.remove()

        self.assertEqual(len(removed.calls), 1)
        self.assertIsNone(subscription.get_subscription_info())
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 0)

    async def test_overlapping_removal_and_update_while_removal_pending_are_rejected_without_side_effects(self):
        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        await subscription.subscribe(events=EVENT_FILTERS)
        confirmed = subscription.get_subscription_info()

        removed = RecordingHandler()
        failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionRemoved, removed)
        self.web_socket_client.on(WebSocketEvents.removeSubscriptionError, failed)

        self.web_socket_client._responder = None
        await subscription.remove()
        self.assertEqual(len(self.web_socket_client.sent_messages), 2)

        with self.assertRaises(Exception):
            await subscription.remove()
        with self.assertRaises(Exception):
            await subscription.update(events=OTHER_FILTERS)

        self.assertEqual(len(self.web_socket_client.sent_messages), 2)
        self.assertIs(subscription.get_subscription_info(), confirmed)
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 1)
        self.assertEqual(removed.calls, [])
        self.assertEqual(failed.calls, [])

        pending_request = self.web_socket_client.sent_messages[1]
        self.web_socket_client.trigger(
            WebSocketEvents.receiveMessage, json.dumps(removal_response(pending_request))
        )
        self.assertEqual(len(removed.calls), 1)
        self.assertEqual(failed.calls, [])
        self.assertIsNone(subscription.get_subscription_info())
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 0)

    async def test_duplicate_and_late_responses_after_completion_produce_no_events_or_changes(self):
        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        await subscription.subscribe(events=EVENT_FILTERS)
        creation_request = self.web_socket_client.sent_messages[0]

        updated = RecordingHandler()
        removed = RecordingHandler()
        failed = RecordingHandler()
        remove_failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionUpdated, updated)
        self.web_socket_client.on(WebSocketEvents.subscriptionRemoved, removed)
        self.web_socket_client.on(WebSocketEvents.updateSubscriptionError, failed)
        self.web_socket_client.on(WebSocketEvents.removeSubscriptionError, remove_failed)

        self.web_socket_client._responder = update_response
        await subscription.update(events=OTHER_FILTERS)
        self.assertEqual(len(updated.calls), 1)
        stored = subscription.get_subscription_info()

        update_request = self.web_socket_client.sent_messages[1]
        self.web_socket_client.trigger(
            WebSocketEvents.receiveMessage, json.dumps(update_response(update_request))
        )
        self.web_socket_client.trigger(
            WebSocketEvents.receiveMessage, json.dumps(creation_response(creation_request))
        )
        self.assertEqual(len(updated.calls), 1)
        self.assertIs(subscription.get_subscription_info(), stored)
        self.assertEqual(failed.calls, [])
        self.assertEqual(removed.calls, [])

        self.web_socket_client._responder = removal_response
        await subscription.remove()
        self.assertEqual(len(removed.calls), 1)
        self.assertIsNone(subscription.get_subscription_info())

        removal_request = self.web_socket_client.sent_messages[2]
        self.web_socket_client.trigger(
            WebSocketEvents.receiveMessage, json.dumps(removal_response(removal_request))
        )
        self.web_socket_client.trigger(
            WebSocketEvents.receiveMessage, json.dumps(update_response(update_request))
        )
        self.assertEqual(len(removed.calls), 1)
        self.assertEqual(len(updated.calls), 1)
        self.assertEqual(failed.calls, [])
        self.assertEqual(remove_failed.calls, [])
        self.assertIsNone(subscription.get_subscription_info())
        self.assertEqual(self.web_socket_client.receive_message_listener_count, 0)

    async def test_responses_correlated_by_message_id_regardless_of_type(self):
        self.web_socket_client._responder = creation_response
        subscription = WebSocketSubscription(self.web_socket_client)
        await subscription.subscribe(events=EVENT_FILTERS)

        updated = RecordingHandler()
        removed = RecordingHandler()
        failed = RecordingHandler()
        remove_failed = RecordingHandler()
        self.web_socket_client.on(WebSocketEvents.subscriptionUpdated, updated)
        self.web_socket_client.on(WebSocketEvents.subscriptionRemoved, removed)
        self.web_socket_client.on(WebSocketEvents.updateSubscriptionError, failed)
        self.web_socket_client.on(WebSocketEvents.removeSubscriptionError, remove_failed)

        self.web_socket_client._responder = lambda request: update_response(
            request, message_type="ClientResponse"
        )
        await subscription.update(events=OTHER_FILTERS)

        self.assertEqual(len(updated.calls), 1)
        self.assertEqual(failed.calls, [])
        self.assertIsNotNone(subscription.get_subscription_info())

        self.web_socket_client._responder = lambda request: removal_response(
            request, message_type="ClientResponse"
        )
        await subscription.remove()

        self.assertEqual(len(removed.calls), 1)
        self.assertEqual(failed.calls, [])
        self.assertEqual(remove_failed.calls, [])
        self.assertIsNone(subscription.get_subscription_info())


if __name__ == "__main__":
    unittest.main()
