from ringcentral import SDK
from dotenv import load_dotenv
import asyncio
import os

# from config import USERNAME, EXTENSION, PASSWORD, APP_KEY, APP_SECRET, SERVER

def on_message(msg):
    print(msg)


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
        await web_socket_client.create_new_connection()
        print("\n New WebSocket connection created:")
        print(web_socket_client.get_connection_info())
        print("\n Creating subscription...")
        sub = await web_socket_client.create_subscription(
            ["/restapi/v1.0/account/~/extension/~/presence"]
        )
        # To update sub: await web_socket_client.update_subscription(sub, events) OR sub.update(events)
        # To remove sub: await web_socket_client.remove_subscription(sub) OR sub.remove()
        
        # Test
        # Go and change your extension status. The notification info will be received and printed here
        while True:
            message = await web_socket_client.get_connection().recv()
            print("\n receiving message: \n")
            print(message)
            await asyncio.sleep(0.5)
    except KeyboardInterrupt:
        print("\nWebSocket connection closed.")
        print("Stopped by User")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
