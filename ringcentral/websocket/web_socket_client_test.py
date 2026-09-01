import asyncio
import contextlib
import json
import unittest
import uuid
from unittest import mock

from .events import WebSocketEvents
from .web_socket_client import WebSocketClient


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json_dict(self):
        return self._payload


class FakePlatform:
    def post(self, path, body=None):
        return FakeResponse({
            "uri": "wss://fake-websocket",
            "ws_access_token": "fake-ws-token",
        })


class FakeWebSocket:
    def __init__(self):
        self.sent = []
        self.received = []
        self.closed = False
        self._fail_next_recv = False
        self._receive_error = None
        self._frames = asyncio.Queue()

    def fail_next_receive(self, error):
        self._fail_next_recv = True
        self._receive_error = error

    def push(self, frame):
        self._frames.put_nowait(frame)

    def has_pending_frames(self):
        return self._frames.qsize() > 0

    async def recv(self):
        if self._fail_next_recv:
            self._fail_next_recv = False
            raise self._receive_error
        frame = await self._frames.get()
        if frame is None:
            raise ConnectionResetError("connection closed")
        self.received.append(frame)
        return frame

    async def send(self, message):
        self.sent.append(message)

    async def close(self):
        self.closed = True
        self._frames.put_nowait(None)


class RecordingHandler:
    def __init__(self, error=None):
        self.calls = []
        self.error = error

    def __call__(self, *args):
        self.calls.append(args)
        if self.error is not None:
            raise self.error


EVENT_FILTERS = ["/restapi/v1.0/account/~/extension/~/presence"]


def subscription_creation_frame(message_id):
    return json.dumps([
        {
            "type": "ClientRequest",
            "messageId": message_id,
            "status": 200,
        },
        {
            "uri": "/restapi/v1.0/subscription/fake-subscription",
            "id": "fake-subscription",
            "status": "Active",
            "eventFilters": EVENT_FILTERS,
            "deliveryMode": {"transportType": "WebSocket"},
        },
    ])


def server_notification_frame():
    return json.dumps([
        {
            "type": "ServerNotification",
            "messageId": str(uuid.uuid4()),
        },
        {
            "uri": "/restapi/v1.0/subscription/fake-subscription",
            "event": {"/restapi/v1.0/account/~/extension/~/presence": {"activeCalls": []}},
        },
    ])


class WebSocketClientTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = WebSocketClient(FakePlatform())

    async def start_receive_loop(self):
        fake_socket = FakeWebSocket()

        async def connect(uri):
            return fake_socket

        patcher = mock.patch("websockets.connect", connect)
        patcher.start()
        self.addCleanup(patcher.stop)
        connection_task = asyncio.create_task(self.client.create_new_connection())
        return fake_socket, connection_task

    async def wait_until(self, predicate, limit=100):
        for _ in range(limit):
            if predicate():
                return
            await asyncio.sleep(0)
        self.fail("condition was not met before the spin limit")

    async def wait_until_frames_delivered(self, fake_socket):
        await self.wait_until(lambda: not fake_socket.has_pending_frames())

    async def stop_receive_loop(self, connection_task):
        connection_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await connection_task

    async def test_failing_handler_does_not_stop_delivery_to_remaining_handlers(self):
        failing = RecordingHandler(error=RuntimeError("handler failure"))
        healthy = RecordingHandler()
        receive_errors = RecordingHandler()
        connection_errors = RecordingHandler()
        self.client.on(WebSocketEvents.receiveMessage, failing)
        self.client.on(WebSocketEvents.receiveMessage, healthy)
        self.client.on(WebSocketEvents.receiveMessageError, receive_errors)
        self.client.on(WebSocketEvents.createConnectionError, connection_errors)

        fake_socket, connection_task = await self.start_receive_loop()
        fake_socket.push("[/heartbeat]")
        fake_socket.push("raw-message")
        await self.wait_until_frames_delivered(fake_socket)
        await self.stop_receive_loop(connection_task)

        self.assertEqual(failing.calls, [("raw-message",)])
        self.assertEqual(healthy.calls, [("raw-message",)])
        self.assertEqual(len(receive_errors.calls), 1)
        self.assertEqual(len(receive_errors.calls[0]), 1)
        self.assertIs(receive_errors.calls[0][0], failing.error)
        self.assertEqual(connection_errors.calls, [])

    async def test_failing_handler_without_error_observers_does_not_stop_reception(self):
        failing = RecordingHandler(error=RuntimeError("handler failure"))
        healthy = RecordingHandler()
        self.client.on(WebSocketEvents.receiveMessage, failing)
        self.client.on(WebSocketEvents.receiveMessage, healthy)

        fake_socket, connection_task = await self.start_receive_loop()
        fake_socket.push("[/heartbeat]")
        fake_socket.push("raw-message")
        await self.wait_until_frames_delivered(fake_socket)
        await self.stop_receive_loop(connection_task)

        self.assertEqual(healthy.calls, [("raw-message",)])

    async def test_future_messages_continue_and_failed_handler_remains_registered(self):
        failing = RecordingHandler(error=RuntimeError("handler failure"))
        healthy = RecordingHandler()
        receive_errors = RecordingHandler()
        self.client.on(WebSocketEvents.receiveMessage, failing)
        self.client.on(WebSocketEvents.receiveMessage, healthy)
        self.client.on(WebSocketEvents.receiveMessageError, receive_errors)

        fake_socket, connection_task = await self.start_receive_loop()
        fake_socket.push("[/heartbeat]")
        fake_socket.push("first-message")
        fake_socket.push("second-message")
        await self.wait_until_frames_delivered(fake_socket)
        await self.stop_receive_loop(connection_task)

        self.assertEqual(failing.calls, [("first-message",), ("second-message",)])
        self.assertEqual(healthy.calls, [("first-message",), ("second-message",)])
        self.assertEqual(
            [call[0] for call in receive_errors.calls],
            [failing.error, failing.error],
        )

    async def test_each_failing_handler_produces_its_own_error_event(self):
        first = RecordingHandler(error=RuntimeError("first failure"))
        second = RecordingHandler(error=ValueError("second failure"))
        healthy = RecordingHandler()
        receive_errors = RecordingHandler()
        self.client.on(WebSocketEvents.receiveMessage, first)
        self.client.on(WebSocketEvents.receiveMessage, healthy)
        self.client.on(WebSocketEvents.receiveMessage, second)
        self.client.on(WebSocketEvents.receiveMessageError, receive_errors)

        fake_socket, connection_task = await self.start_receive_loop()
        fake_socket.push("[/heartbeat]")
        fake_socket.push("raw-message")
        await self.wait_until_frames_delivered(fake_socket)
        await self.stop_receive_loop(connection_task)

        self.assertEqual(first.calls, [("raw-message",)])
        self.assertEqual(second.calls, [("raw-message",)])
        self.assertEqual(healthy.calls, [("raw-message",)])
        self.assertEqual(
            [call[0] for call in receive_errors.calls],
            [first.error, second.error],
        )

    async def test_subscription_parser_failures_are_isolated_and_reception_continues(self):
        raw_messages = RecordingHandler()
        receive_errors = RecordingHandler()
        notifications = RecordingHandler()
        subscription_created = RecordingHandler()
        connection_errors = RecordingHandler()
        connection_created = RecordingHandler()
        self.client.on(WebSocketEvents.receiveMessage, raw_messages)
        self.client.on(WebSocketEvents.receiveMessageError, receive_errors)
        self.client.on(WebSocketEvents.receiveSubscriptionNotification, notifications)
        self.client.on(WebSocketEvents.subscriptionCreated, subscription_created)
        self.client.on(WebSocketEvents.createConnectionError, connection_errors)
        self.client.on(WebSocketEvents.connectionCreated, connection_created)

        fake_socket, connection_task = await self.start_receive_loop()
        fake_socket.push("[/heartbeat]")
        await self.wait_until(lambda: len(connection_created.calls) == 1)

        await self.client.create_subscription(events=EVENT_FILTERS)

        request = json.loads(fake_socket.sent[0])
        creation_frame = subscription_creation_frame(request[0]["messageId"])
        notification_frame = server_notification_frame()
        fake_socket.push(creation_frame)
        fake_socket.push("not-json")
        fake_socket.push("{}")
        fake_socket.push("[]")
        fake_socket.push(notification_frame)
        await self.wait_until_frames_delivered(fake_socket)
        await self.stop_receive_loop(connection_task)

        self.assertEqual(len(subscription_created.calls), 1)
        subscription = subscription_created.calls[0][0]
        self.assertEqual(subscription.get_subscription_info()[1]["id"], "fake-subscription")

        self.assertEqual(raw_messages.calls, [
            (creation_frame,),
            ("not-json",),
            ("{}",),
            ("[]",),
            (notification_frame,),
        ])
        self.assertEqual(len(receive_errors.calls), 3)
        self.assertIsInstance(receive_errors.calls[0][0], json.JSONDecodeError)
        self.assertIsInstance(receive_errors.calls[1][0], KeyError)
        self.assertIsInstance(receive_errors.calls[2][0], IndexError)
        self.assertEqual(len(notifications.calls), 1)
        self.assertEqual(notifications.calls[0][0], json.loads(notification_frame))
        self.assertEqual(connection_errors.calls, [])

    async def test_failing_error_observer_does_not_block_other_error_observers_or_reception(self):
        failing_receive = RecordingHandler(error=RuntimeError("handler failure"))
        healthy_receive = RecordingHandler()
        failing_error_observer = RecordingHandler(error=RuntimeError("observer failure"))
        recording_error_observer = RecordingHandler()
        self.client.on(WebSocketEvents.receiveMessage, failing_receive)
        self.client.on(WebSocketEvents.receiveMessage, healthy_receive)
        self.client.on(WebSocketEvents.receiveMessageError, failing_error_observer)
        self.client.on(WebSocketEvents.receiveMessageError, recording_error_observer)

        fake_socket, connection_task = await self.start_receive_loop()
        fake_socket.push("[/heartbeat]")
        fake_socket.push("first-message")
        fake_socket.push("second-message")
        await self.wait_until_frames_delivered(fake_socket)
        await self.stop_receive_loop(connection_task)

        self.assertEqual(recording_error_observer.calls, [
            (failing_receive.error,),
            (failing_receive.error,),
        ])
        self.assertEqual(failing_receive.calls, [("first-message",), ("second-message",)])
        self.assertEqual(healthy_receive.calls, [("first-message",), ("second-message",)])

    async def test_unrelated_event_dispatch_semantics_remain_unchanged(self):
        failing = RecordingHandler(error=RuntimeError("unrelated failure"))
        healthy = RecordingHandler()
        self.client.on(WebSocketEvents.subscriptionCreated, failing)
        self.client.on(WebSocketEvents.subscriptionCreated, healthy)

        with self.assertRaises(RuntimeError):
            self.client.trigger(WebSocketEvents.subscriptionCreated, self.client)

        self.assertEqual(failing.calls, [(self.client,)])
        self.assertEqual(healthy.calls, [])

    async def test_recv_failure_after_handshake_reports_receive_error_and_cleans_up(self):
        receive_error = RuntimeError("receive failure")
        receive_errors = RecordingHandler()
        connection_errors = RecordingHandler()
        self.client.on(WebSocketEvents.receiveMessageError, receive_errors)
        self.client.on(WebSocketEvents.createConnectionError, connection_errors)

        sockets = []

        def on_connected(*_):
            sockets[0].fail_next_receive(receive_error)

        self.client.on(WebSocketEvents.connectionCreated, on_connected)

        fake_socket, connection_task = await self.start_receive_loop()
        fake_socket.push("[/heartbeat]")
        sockets.append(fake_socket)

        result = await connection_task

        self.assertIsNone(result)
        self.assertEqual(len(receive_errors.calls), 1)
        self.assertEqual(len(receive_errors.calls[0]), 1)
        self.assertIs(receive_errors.calls[0][0], receive_error)
        self.assertEqual(connection_errors.calls, [])
        self.assertFalse(self.client._is_ready)
        await self.wait_until(lambda: self.client._heartbeat_task.done())
        self.assertTrue(self.client._heartbeat_task.cancelled())

    async def test_receive_loop_cancellation_marks_client_not_ready_and_cancels_heartbeat(self):
        receive_errors = RecordingHandler()
        connection_errors = RecordingHandler()
        self.client.on(WebSocketEvents.receiveMessageError, receive_errors)
        self.client.on(WebSocketEvents.createConnectionError, connection_errors)

        fake_socket, connection_task = await self.start_receive_loop()
        fake_socket.push("[/heartbeat]")
        await self.wait_until(lambda: self.client._is_ready)
        self.assertTrue(self.client._is_ready)

        await self.stop_receive_loop(connection_task)

        self.assertFalse(self.client._is_ready)
        await self.wait_until(lambda: self.client._heartbeat_task.done())
        self.assertTrue(self.client._heartbeat_task.cancelled())
        self.assertEqual(receive_errors.calls, [])
        self.assertEqual(connection_errors.calls, [])

    async def test_intentional_close_performs_cleanup_without_receive_error(self):
        receive_errors = RecordingHandler()
        connection_errors = RecordingHandler()
        close_errors = RecordingHandler()
        self.client.on(WebSocketEvents.receiveMessageError, receive_errors)
        self.client.on(WebSocketEvents.createConnectionError, connection_errors)
        self.client.on(WebSocketEvents.closeConnectionError, close_errors)

        fake_socket, connection_task = await self.start_receive_loop()
        fake_socket.push("[/heartbeat]")
        await self.wait_until(lambda: self.client._is_ready)

        await self.client.close_connection()
        result = await connection_task

        self.assertIsNone(result)
        self.assertTrue(fake_socket.closed)
        self.assertFalse(self.client._is_ready)
        await self.wait_until(lambda: self.client._heartbeat_task.done())
        self.assertTrue(self.client._heartbeat_task.cancelled())
        self.assertEqual(receive_errors.calls, [])
        self.assertEqual(connection_errors.calls, [])
        self.assertEqual(close_errors.calls, [])

    async def test_connection_establishment_failure_retains_create_connection_error(self):
        connect_error = RuntimeError("connect failure")
        receive_errors = RecordingHandler()
        connection_errors = RecordingHandler()
        self.client.on(WebSocketEvents.receiveMessageError, receive_errors)
        self.client.on(WebSocketEvents.createConnectionError, connection_errors)

        async def connect(uri):
            raise connect_error

        with mock.patch("websockets.connect", connect):
            with self.assertRaises(RuntimeError):
                await self.client.create_new_connection()

        self.assertTrue(connection_errors.calls)
        for call in connection_errors.calls:
            self.assertIs(call[0], connect_error)
        self.assertEqual(receive_errors.calls, [])

    async def test_initial_handshake_failure_retains_create_connection_error(self):
        handshake_error = RuntimeError("handshake failure")
        receive_errors = RecordingHandler()
        connection_errors = RecordingHandler()
        self.client.on(WebSocketEvents.receiveMessageError, receive_errors)
        self.client.on(WebSocketEvents.createConnectionError, connection_errors)

        fake_socket = FakeWebSocket()
        fake_socket.fail_next_receive(handshake_error)

        async def connect(uri):
            return fake_socket

        with mock.patch("websockets.connect", connect):
            with self.assertRaises(RuntimeError):
                await self.client.create_new_connection()

        self.assertTrue(connection_errors.calls)
        for call in connection_errors.calls:
            self.assertIs(call[0], handshake_error)
        self.assertEqual(receive_errors.calls, [])
        self.assertFalse(self.client._is_ready)
        self.assertIsNone(self.client._heartbeat_task)


if __name__ == "__main__":
    unittest.main()
