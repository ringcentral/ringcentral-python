from ringcentral import SDK
from dotenv import dotenv_values

env = dotenv_values(".env")

def main():
    sdk = SDK(env['RINGCENTRAL_CLIENT_ID'], env['RINGCENTRAL_CLIENT_SECRET'], env['RINGCENTRAL_SERVER_URL'])
    platform = sdk.platform()
    platform.login(jwt = env['RINGCENTRAL_JWT_TOKEN'])

    params = {'from': {'phoneNumber': env['RINGCENTRAL_SENDER']},'to': [{'phoneNumber': env['RINGCENTRAL_RECEIVER']}],'text': "SMS message"}
    response = platform.post('/restapi/v1.0/account/~/extension/~/sms', params)

    print('Sent SMS: ' + response.json().uri)

if __name__ == '__main__':
    main()
