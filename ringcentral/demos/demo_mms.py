import ssl
import certifi
import urllib.request
from dotenv import dotenv_values
from ringcentral import SDK

env = dotenv_values(".env")

def main():
    sdk = SDK(env['RINGCENTRAL_CLIENT_ID'], env['RINGCENTRAL_CLIENT_SECRET'], env['RINGCENTRAL_SERVER_URL'])
    platform = sdk.platform()
    platform.login(jwt = env['RINGCENTRAL_JWT_TOKEN'])

    builder = sdk.create_multipart_builder()
    builder.set_body({
        'from': {'phoneNumber': env['RINGCENTRAL_SENDER']},
        'to': [{'phoneNumber': env['RINGCENTRAL_RECEIVER']}],
        'text': 'MMS from Python'  # this is optional
    })
    attachment = (
        'test.png',
        urllib.request.urlopen('https://developers.ringcentral.com/assets/images/ico_case_crm.png', 
                               context=ssl.create_default_context(cafile=certifi.where())).read(),
        'image/png'
    )
    builder.add(attachment)

    request = builder.request('/account/~/extension/~/sms')
    response = platform.send_request(request)
    print('Sent MMS: ' + response.json().uri)

if __name__ == '__main__':
    main()
