
class WebSocketEvents:
    """
        WebSocketEvents class representing various events related to WebSocket communication.

        Attributes:
            getTokenError (str): Event triggered when an error occurs while retrieving the WebSocket token.
            createConnectionError (str): Event triggered when an error occurs while creating a WebSocket connection.
            connectionCreated (str): Event triggered when a WebSocket connection is successfully created.
            closeConnectionError (str): Event triggered when an error occurs while closing a WebSocket connection.
            recoverConnectionError (str): Event triggered when an error occurs while recovering a WebSocket connection.
            receiveMessage (str): Event triggered when a message is received over the WebSocket connection.
            receiveMessageError (str): Event triggered when an exception occurs while receiving a message or while dispatching a received message to a receive-message handler. Its sole argument is the original exception. Unlike createConnectionError, it is not used for connection creation or the initial handshake.
            sendMessageError (str): Event triggered when an error occurs while sending a message over the WebSocket connection.
            connectionNotReady (str): Event triggered when attempting to perform an action while the WebSocket connection is not ready.
            createSubscriptionError (str): Event triggered when an error occurs while creating a subscription.
            updateSubscriptionError (str): Event triggered when an error occurs while updating a subscription.
            removeSubscriptionError (str): Event triggered when an error occurs while removing a subscription.
            subscriptionCreated (str): Event triggered when a subscription is successfully created.
            subscriptionUpdated (str): Event triggered when a subscription is successfully updated.
            subscriptionRemoved (str): Event triggered when a subscription is successfully removed.
            receiveSubscriptionNotification (str): Event triggered when a subscription notification is received.
    """
    getTokenError = 'getTokenError'
    createConnectionError = 'createConnectionError'
    connectionCreated = 'connectionCreated'
    closeConnectionError = 'closeConnectionError'
    recoverConnectionError = 'recoverConnectionError'
    receiveMessage = 'receiveMessage'
    receiveMessageError = 'receiveMessageError'
    sendMessageError = 'sendMessageError'
    connectionNotReady = 'connectionNotReady'
    createSubscriptionError = 'createSubscriptionError'
    updateSubscriptionError = 'updateSubscriptionError'
    removeSubscriptionError = 'removeSubscriptionError'
    subscriptionCreated = 'subscriptionCreated'
    subscriptionUpdated = 'subscriptionUpdated'
    subscriptionRemoved = 'subscriptionRemoved'
    receiveSubscriptionNotification = 'receiveSubscriptionNotification'

    def __init__(self):
        pass
