from __future__ import print_function
from dotenv import load_dotenv
from ringcentral import SDK
import json
import uuid
import os
import asyncio

async def main():
    try:
        load_dotenv(override=True)
        sdk = SDK(
            os.environ['RINGCENTRAL_CLIENT_ID'],
            os.environ["RINGCENTRAL_CLIENT_SECRET"],
            os.environ["RINGCENTRAL_SERVER_URL"],
        )
        platform = sdk.platform()
        platform.login(jwt=os.environ["RINGCENTRAL_JWT_TOKEN"])

        # Create new websocket connection
        web_socket_client = sdk.create_web_socket_client()
        await web_socket_client.create_new_connection()
        print("\n New WebSocket connection created:")
        print(web_socket_client.get_connection_info())
        
        # Send API call to RingCentral WebSocket Gateway, just like using HTTPS Gateway
        messageId = str(uuid.uuid4())
        print(messageId)
        requestBodyJson = json.dumps(
            [
                {
                    "type": "ClientRequest",
                    "messageId": messageId,
                    "method": "GET",
                    "path": "/restapi/v1.0/account/~/extension/~",
                }
            ]
        )
        ws_connection = web_socket_client.get_connection()
        print(ws_connection)
        await ws_connection.send(requestBodyJson)
        response = await ws_connection.recv()
        print("\n User email:\n")
        print(json.loads(response)[1]['contact']['email'])
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        # Close websocket connection
        web_socket_client.close_connection()
        print("\nWebSocket connection closed.")
        print("Stopped by User")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
