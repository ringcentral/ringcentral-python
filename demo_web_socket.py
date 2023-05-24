from __future__ import print_function
from dotenv import dotenv_values
from ringcentral import SDK
from ringcentral.websocket.web_socket_client import WebSocketClient

env = dotenv_values(".env")


def main():
    sdk = SDK(
        env["RINGCENTRAL_CLIENT_ID"],
        env["RINGCENTRAL_CLIENT_SECRET"],
        env["RINGCENTRAL_SERVER_URL"],
    )
    platform = sdk.platform()
    platform.login(jwt=env["RINGCENTRAL_JWT_TOKEN"])

    # Get websocket token
    web_socket_client = WebSocketClient(platform)
    response = web_socket_client.get_web_socket_token()
    print(response)

    # Open websocket connection
    open_connection_response = web_socket_client.open_connection(
        response["uri"], response["ws_access_token"]
    )
    web_socket_connection = open_connection_response["connection"]
    print("\nNew web socket connection opened as:")
    print(type(web_socket_connection))
    print("\nConnection details:")
    print(open_connection_response["connection_details"])

    # Close websocket connection
    web_socket_client.close_connection(web_socket_connection)
    print("\nWeb socket connection closed.")


if __name__ == "__main__":
    main()
