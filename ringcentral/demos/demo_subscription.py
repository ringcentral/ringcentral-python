from dotenv import load_dotenv
import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))  # Add the project root to sys.path
from ringcentral.websocket.events import WebSocketEvents
from ringcentral import SDK

def on_notification(message):
    print("\n Subscription notification:\n")
    print(message)

def on_sub_created(sub):
    print("\n Subscription created:\n")
    print(sub.get_subscription_info())
    print("\n Please go and change your user status \n")

def on_ws_created(web_socket_client):
    print("\n New WebSocket connection created:")
    print(web_socket_client.get_connection_info())

async def main():
    load_dotenv(override=True)
    sdk = SDK(
        os.environ['RINGCENTRAL_CLIENT_ID'],
        os.environ["RINGCENTRAL_CLIENT_SECRET"],
        os.environ["RINGCENTRAL_SERVER_URL"],
    )
    platform = sdk.platform()
    platform.login(jwt=os.environ["RINGCENTRAL_JWT_TOKEN"])

    try:
        web_socket_client = sdk.create_web_socket_client()
        web_socket_client.on(WebSocketEvents.connectionCreated, on_ws_created)
        web_socket_client.on(WebSocketEvents.subscriptionCreated, on_sub_created)
        web_socket_client.on(WebSocketEvents.receiveSubscriptionNotification, on_notification)
        await asyncio.gather(
            web_socket_client.create_new_connection(), 
            web_socket_client.create_subscription(["/restapi/v1.0/account/~/extension/~/presence"])
        )
    except KeyboardInterrupt:
        print("Stopped by User")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
