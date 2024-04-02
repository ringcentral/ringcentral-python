
class Events:
    """
    Class representing different types of events that can occur.

    Attributes:
        connectionError (str): Represents an event indicating a connection error.
        notification (str): Represents an event for receiving notifications.
        subscribeSuccess (str): Represents a successful subscription event.
        subscribeError (str): Represents an error event during subscription.
        renewSuccess (str): Represents a successful renewal event.
        renewError (str): Represents an error event during renewal.
        removeSuccess (str): Represents a successful removal event.
        removeError (str): Represents an error event during removal.
    """
    connectionError = 'connectionError'
    notification = 'notification'
    subscribeSuccess = 'subscribeSuccess'
    subscribeError = 'subscribeError'
    renewSuccess = 'renewSuccess'
    renewError = 'renewError'
    removeSuccess = 'removeSuccess'
    removeError = 'removeError'

    def __init__(self):
        pass
