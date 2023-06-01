import unittest
import json
import os
from dotenv import load_dotenv
from ringcentral import SDK
from unittest import IsolatedAsyncioTestCase
from .web_socket_subscription import *


# This test suite uses real case. It needs .env credentials setup.
class TestSubscription(IsolatedAsyncioTestCase):
    def setUp(self):
        load_dotenv(override=True)
        sdk = SDK(
            os.environ['RINGCENTRAL_CLIENT_ID'],
            os.environ["RINGCENTRAL_CLIENT_SECRET"],
            os.environ["RINGCENTRAL_SERVER_URL"],
        )
        platform = sdk.platform()
        platform.login(jwt=os.environ["RINGCENTRAL_JWT_TOKEN"])
        self._sdk = sdk

    async def test_web_socket_create(self):
        # Act
        # Create new websocket connection
        web_socket_client = self._sdk.create_web_socket_client()
        await web_socket_client.create_new_connection()
        result_status=json.loads(web_socket_client.get_connection_info()['connection_details'])[0]['status']

        # Assert
        try:
            self.assertEqual(200, result_status)

        # Clean up
        finally:
            await web_socket_client.close_connection()

    async def test_web_socket_subscription_create(self):
        # Act
        # Create new websocket connection
        web_socket_client = self._sdk.create_web_socket_client()
        await web_socket_client.create_new_connection()
        
        # Create new subscription
        sub = await web_socket_client.create_subscription(
            ["/restapi/v1.0/account/~/extension/~/presence"]
        )
        result_status=sub.get_subscription_info()[0]['status']
        
        # Assert
        try:
            self.assertEqual(200, result_status)

        # Clean up
        finally:
            await sub.remove()
            await web_socket_client.close_connection()

if __name__ == "__main__":
    unittest.main()
