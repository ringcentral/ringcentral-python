
class Events:
    """
    Events class representing various event types.

    Attributes:
        refreshSuccess (str): Represents a successful refresh event.
        refreshError (str): Represents an error during refresh.
        loginSuccess (str): Represents a successful login event.
        loginError (str): Represents an error during login.
        logoutSuccess (str): Represents a successful logout event.
        logoutError (str): Represents an error during logout.
    """
    refreshSuccess = 'refreshSuccess'
    refreshError = 'refreshError'
    loginSuccess = 'loginSuccess'
    loginError = 'loginError'
    logoutSuccess = 'logoutSuccess'
    logoutError = 'logoutError'

    def __init__(self):
        pass
