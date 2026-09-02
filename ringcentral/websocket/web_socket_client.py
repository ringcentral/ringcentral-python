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
        self._heartbeat_task = None
        self._send_attempt_counter = 0
        self._subscription = None

    async def create_new_connection(self):
        """
        Creates a new WebSocket connection.

        Returns:
            Any: Response object containing the result of the connection creation.

        Raises:
            Exception: If any error occurs during the process.

        Note:
            - Retrieves the WebSocket token using `get_web_socket_token`.
            - Attempts to open a WebSocket connection using the retrieved token's URI and access token.
            - Triggers the createConnectionError event if an error occurs and raises the exception.
        """
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
        """
            Retrieves a WebSocket token.

            Returns:
                dict: WebSocket token containing URI and access token.

            Raises:
                Exception: If any error occurs during the process.

            Note:
                - Sends a POST request to the '/restapi/oauth/wstoken' endpoint to obtain the WebSocket token.
                - Returns the WebSocket token as a dictionary containing the URI and access token.
                - Triggers the getTokenError event if an error occurs and raises the exception.
        """
        try:
            response = self._platform.post("/restapi/oauth/wstoken", body={})
            return response.json_dict()
        except Exception as e:
            self.trigger(WebSocketEvents.getTokenError, e)
            raise

    async def open_connection(self, ws_uri, ws_access_token):
        """
            Opens a WebSocket connection.

            Args:
                ws_uri (str): The WebSocket URI.
                ws_access_token (str): The access token for WebSocket authentication.

            Raises:
                Exception: If any error occurs during the process.

            Note:
                - Attempts to establish a WebSocket connection to the provided URI with the given access token.
                - Upon successful connection, sets up a heartbeat mechanism to maintain the connection.
                - Triggers the connectionCreated event upon successful connection establishment.
                - Listens for incoming messages and triggers the receiveMessage event for each received message.
                - Isolates receive-message handler failures so a handler that raises does not stop delivery to the remaining handlers or reception of future messages; each failure triggers the receiveMessageError event with the original exception.
                - Triggers the createConnectionError event if an error occurs while establishing the connection or during the initial handshake, and raises the exception.
                - A failure from receiving messages after the initial handshake triggers the receiveMessageError event once; it is not reported as a connection-creation error and does not propagate to the connection-setup or recovery wrappers.
                - When the receive loop terminates (receive failure, cancellation, or intentional closure), the client is marked not ready and its heartbeat task is cancelled.
                - An intentional closure does not trigger the receiveMessageError event.
        """
        self._done = False
        try:
            websocket = await websockets.connect(
                f"{ws_uri}?access_token={ws_access_token}"
            )
            connectionMessage = await websocket.recv()
        except Exception as e:
            self.trigger(WebSocketEvents.createConnectionError, e)
            raise

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
        self._heartbeat_task = timer

        try:
            await asyncio.sleep(0)
            while True:
                message = await websocket.recv()
                self.trigger(WebSocketEvents.receiveMessage, message)
                await asyncio.sleep(0)
        except Exception as e:
            if not self._done:
                self.trigger(WebSocketEvents.receiveMessageError, e)
        finally:
            self._is_ready = False
            timer.cancel()

    def trigger(self, event, *args, **kw):
        """
            Triggers the handlers registered for an event.

            Args:
                event (str): The event to trigger.
                args: The event arguments.
                kw: The event keyword arguments.

            Returns:
                bool: True if any handler was triggered, False if the event has no handlers.

            Note:
                - receiveMessage handlers are invoked independently: if one raises, the remaining handlers still receive the same raw message and one receiveMessageError event is triggered with the original exception.
                - receiveMessageError handlers are also invoked independently: a failing error handler is contained so error reporting and reception continue.
                - Every other event keeps the default dispatch behavior.
        """
        if event == WebSocketEvents.receiveMessage:
            return self._trigger_receive_message(*args, **kw)
        if event == WebSocketEvents.receiveMessageError:
            return self._trigger_receive_message_error(*args, **kw)
        return Observable.trigger(self, event, *args, **kw)

    def _trigger_receive_message(self, *args, **kw):
        handlers = list(self.events.get(WebSocketEvents.receiveMessage) or [])
        if not handlers:
            return False
        for handler in handlers:
            try:
                handler(*args, **kw)
            except Exception as e:
                self.trigger(WebSocketEvents.receiveMessageError, e)
        return True

    def _trigger_receive_message_error(self, *args, **kw):
        handlers = list(self.events.get(WebSocketEvents.receiveMessageError) or [])
        if not handlers:
            return False
        for handler in handlers:
            try:
                handler(*args, **kw)
            except Exception:
                pass
        return True

    def get_connection_info(self):
        return self._web_socket

    def get_connection(self):
        return self._web_socket["connection"]

    async def close_connection(self):
        """
            Closes the WebSocket connection.

            Raises:
                Exception: If any error occurs during the process.

            Note:
                - Sets the `_done` flag to True to signal the termination of the heartbeat mechanism.
                - Sets the `_is_ready` flag to False to indicate that the connection is no longer ready.
                - Retrieves the WebSocket connection using `get_connection`.
                - Closes the WebSocket connection.
                - Triggers the closeConnectionError event if an error occurs during the closing process and raises the exception.
        """
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
        """
            Sends a message over the WebSocket connection.

            Args:
                message (Any): The message to be sent.

            Raises:
                Exception: If any error occurs during the process or if the connection is not ready after multiple attempts.

            Note:
                - Checks if the WebSocket connection is ready (`_is_ready` flag).
                - If the connection is ready, resets the send attempt counter and sends the message.
                - If the connection is not ready, retries after a delay and increments the send attempt counter.
                - If the send attempt counter exceeds a threshold, triggers the connectionNotReady event and raises an exception.
        """
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

    async def create_subscription(self, events):
        """
            Creates a subscription to WebSocket events.

            Args:
                events (list): A required, non-empty list of events to subscribe to.

            Raises:
                Exception: If any error occurs during the process, if events are omitted, None, or empty, if a subscription creation is already in progress, or if a subscription already exists.

            Note:
                - Events are required: an omitted argument is rejected by ordinary Python argument checking, and None or empty events raise "Events are undefined" before any request is sent or any receive listener is attached.
                - The client retains and reuses a single subscription object; a retry after a failed creation and a creation after removal reuse the retained object's existing registration flow with the newly supplied events.
                - Rejects a call while a subscription creation is already in progress with "WebSocket subscription creation is already in progress; wait for subscriptionCreated or createSubscriptionError before retrying".
                - Rejects a call after a subscription has been created with "A WebSocket subscription already exists; use update_subscription() to change its events or remove_subscription() before creating another".
                - Rejections are delivered through the createSubscriptionError event and raised to the caller.
                - If the WebSocket connection is ready (`_is_ready` flag), resets the send attempt counter and registers the retained subscription with the specified events.
                - If the connection is not ready, retries after a delay and increments the send attempt counter.
                - If the send attempt counter exceeds a threshold, triggers the connectionNotReady event and raises an exception.
        """
        try:
            if not events or len(events) == 0:
                raise Exception("Events are undefined")

            if self._subscription is None:
                self._subscription = WebSocketSubscription(self)
            subscription = self._subscription

            if subscription._pending_creation_message_id is not None:
                raise Exception("WebSocket subscription creation is already in progress; wait for subscriptionCreated or createSubscriptionError before retrying")
            if subscription.get_subscription_info() is not None:
                raise Exception("A WebSocket subscription already exists; use update_subscription() to change its events or remove_subscription() before creating another")

            if self._is_ready:
                self._send_attempt_counter = 0
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
        """
            Updates an existing WebSocket subscription with new events.

            Args:
                subscription : The WebSocket subscription to update.
                events (list, optional): A list of events to update the subscription with. Default is None.

            Returns:
                WebSocketSubscription: The updated WebSocket subscription.

            Raises:
                Exception: If any error occurs during the process.

            Note:
                - Updates the specified WebSocket subscription with the new events provided.
                - If the update is successful, returns the updated WebSocket subscription.
                - If an error occurs during the update process, triggers the updateSubscriptionError event and raises an exception.
        """
        try:
            await subscription.update(events)
            return subscription
        except Exception as e:
            self.trigger(WebSocketEvents.updateSubscriptionError, e)
            raise

    async def remove_subscription(self, subscription):
        """
            Removes an existing WebSocket subscription.

            Args:
                subscription : The WebSocket subscription to remove.

            Raises:
                Exception: If any error occurs during the removal process.

            Note:
                - Removes the specified WebSocket subscription.
                - If the removal is successful, the subscription is effectively unsubscribed from the events it was subscribed to.
                - If an error occurs during the removal process, triggers the removeSubscriptionError event and raises an exception.
        """
        try:
            await subscription.remove()
        except Exception as e:
            self.trigger(WebSocketEvents.removeSubscriptionError, e)
            raise


if __name__ == "__main__":
    pass
