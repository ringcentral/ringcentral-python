from __future__ import print_function
from dotenv import dotenv_values
from ringcentral.http.api_exception import ApiException
from ringcentral import SDK


env = dotenv_values(".env")
def main():
    sdk = SDK(env['RINGCENTRAL_CLIENT_ID'], env['RINGCENTRAL_CLIENT_SECRET'], env['RINGCENTRAL_SERVER_URL'])
    platform = sdk.platform()
    platform.login(jwt = env['RINGCENTRAL_JWT_TOKEN'])

    # Simple GET
    response = platform.get('/account/~/extension/~')
    user = response.json()
    user_id = str(user.id)
    print('User loaded ' + user.name + ' (' + user_id + ')')
    print('Headers ' + str(response.response().headers))

    print(type(response.response()._content))

    # Multipart response
    try:
        multipart_response = platform.get('/account/~/extension/' + user_id + ',' + user_id + '/presence').multipart()
        print('Multipart 1\n' + str(multipart_response[0].json_dict()))
        print('Multipart 2\n' + str(multipart_response[1].json_dict()))
    except ApiException as e:
        print('Cannot load multipart')
        print('URL ' + e.api_response().request().url)
        print('Response' + str(e.api_response().json()))


if __name__ == '__main__':
    main()
