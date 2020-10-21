from ringcentral import SDK
from config import USERNAME, EXTENSION, PASSWORD, APP_KEY, APP_SECRET, SERVER

# Before you start
# Rename credentials-sample.ini to credentials.ini
# Edit credentials.ini with information about your app and your creds

sdk = SDK(APP_KEY, APP_SECRET, SERVER)
platform = sdk.platform()
platform.login(USERNAME, EXTENSION, PASSWORD)

res = platform.get('/account/~/extension/~')
print('User loaded ' + res.json().name)
