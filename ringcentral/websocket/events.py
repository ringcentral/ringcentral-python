
class WebSocketEvents:
    getTokenError = 'getTokenError'
    createConnectionError = 'createConnectionError'
    connectionCreated = 'connectionCreated'
    closeConnectionError = 'closeConnectionError'
    recoverConnectionError = 'recoverConnectionError'
    receiveMessage = 'receiveMessage'
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
