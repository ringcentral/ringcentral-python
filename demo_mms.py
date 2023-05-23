import urllib
from dotenv import dotenv_values

#from config import USERNAME, EXTENSION, PASSWORD, APP_KEY, APP_SECRET, SERVER, MOBILE
from ringcentral import SDK

env = dotenv_values(".env")

def main():
    #sdk = SDK(APP_KEY, APP_SECRET, SERVER)
    sdk = SDK(env['RINGCENTRAL_CLIENT_ID'], env['RINGCENTRAL_CLIENT_SECRET'], env['RINGCENTRAL_SERVER_URL'])
    platform = sdk.platform()
    platform.login(jwt = env['RINGCENTRAL_JWT_TOKEN'])

    params = {'from': {'phoneNumber': env['RINGCENTRAL_USERNAME']},'to': [{'phoneNumber': env['RINGCENTRAL_RECEIVER']}],'text': "MMS message"}
    response = platform.post('/restapi/v1.0/account/~/extension/~/mms', params)


    #platform.login(USERNAME, EXTENSION, PASSWORD)

    # Step 1. Get MMS-enabled phone number

    phone_numbers = platform.get('/account/~/extension/~/phone-number', {'perPage': 'max'}).json().records

    mms_number = None

    for phone_number in phone_numbers:
        if 'MmsSender' in phone_number.features:
            mms_number = phone_number.phoneNumber

    print('MMS Phone Number: ' + mms_number)

    # Step 2. Send MMS

    attachment = (
        'test.png',
        urllib.urlopen('https://developers.ringcentral.com/assets/images/ico_case_crm.png').read(),
        'image/png'
    )

    builder = sdk.create_multipart_builder()
    builder.set_body({
        'from': {'phoneNumber': mms_number},
        'to': [{'phoneNumber': phone_number}],
        'text': 'MMS from Python'  # this is optional
    })
    builder.add(attachment)

    request = builder.request('/account/~/extension/~/sms')

    response = platform.send_request(request)
    print('Sent MMS: ' + response.json().uri)


if __name__ == '__main__':
    main()
