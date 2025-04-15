import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)  # Add the project root to sys.path
from dotenv import dotenv_values

from ringcentral import SDK

env = dotenv_values(".env")


def main():
    sdk = SDK(
        env["RINGCENTRAL_CLIENT_ID"],
        env["RINGCENTRAL_CLIENT_SECRET"],
        env["RINGCENTRAL_SERVER_URL"],
    )
    platform = sdk.platform()
    platform.login(jwt=env["RINGCENTRAL_JWT_TOKEN"])

    params = {
        "from": {"phoneNumber": env["RINGCENTRAL_SENDER"]},
        "to": [{"phoneNumber": env["RINGCENTRAL_RECEIVER"]}],
        "text": "SMS message",
    }
    response = platform.post("/restapi/v1.0/account/~/extension/~/sms", params)

    print("Sent SMS: " + response.json().uri)
    print(response.response().status_code)


if __name__ == "__main__":
    main()
