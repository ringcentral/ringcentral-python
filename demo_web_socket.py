from dotenv import load_dotenv
from ringcentral import SDK
from ringcentral.websocket.events import WebSocketEvents
import json
import uuid
import os
import asyncio


def on_message(message):
    print("\n WebSocket message:\n")
    print(json.loads(message))
    print("\n User email:\n")
    print(json.loads(message)[1]["contact"]["email"])


def on_created(web_socket_client):
    print("\n New WebSocket connection created:")
    print(web_socket_client.get_connection_info())


async def send_message(web_socket_client):
    # Send API call to RingCentral WebSocket Gateway, just like using HTTPS Gateway
    messageId = str(uuid.uuid4())
    message = [
        {
            "type": "ClientRequest",
            "messageId": messageId,
            "method": "GET",
            "path": "/restapi/v1.0/account/~/extension/~",
        }
    ]
    await web_socket_client.send_message(message)


async def main():
    try:
        load_dotenv(override=True)
        sdk = SDK(
            os.environ["RINGCENTRAL_CLIENT_ID"],
            os.environ["RINGCENTRAL_CLIENT_SECRET"],
            os.environ["RINGCENTRAL_SERVER_URL"],
        )
        platform = sdk.platform()
        platform.login(jwt=os.environ["RINGCENTRAL_JWT_TOKEN"])

        # Create new websocket connection
        web_socket_client = sdk.create_web_socket_client()
        web_socket_client.on(WebSocketEvents.connectionCreated, on_created)
        web_socket_client.on(WebSocketEvents.receiveMessage, on_message)
        await asyncio.gather(
            web_socket_client.create_new_connection(), 
            send_message(web_socket_client)
        )

    except KeyboardInterrupt:
        print("Stopped by User")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
