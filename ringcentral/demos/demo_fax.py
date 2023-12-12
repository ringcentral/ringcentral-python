import os,time,ssl
from dotenv import load_dotenv
import certifi
import urllib.request
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))  # Add the project root to sys.path
from ringcentral import SDK

load_dotenv()
#env = dotenv_values(".env")

# Send a high resolution fax message to a recipient number
def send_fax():
    try:
        builder = rcsdk.create_multipart_builder()
        builder.set_body({
            'to': [{ 'phoneNumber': RECIPIENT }],
            # To send fax to multiple recipients, add more 'phoneNumber' object. E.g.
            #
            # to: [
            #       { 'phoneNumber': "Recipient1-Phone-Number" },
            #       { 'phoneNumber': "Recipient2-Phone-Number" }
            # ],
            'faxResolution': "High",
            'coverPageText': "This is a demo Fax page from Python"
        })

        attachment = (
            'test.png',
            urllib.request.urlopen('https://www.ringcentral.com/content/dam/rc-2018/en_us/images/logo.jpg', 
                                context=ssl.create_default_context(cafile=certifi.where())).read(),
            'image/png'
        ) 
        builder.add(attachment)
        request = builder.request('/restapi/v1.0/account/~/extension/~/fax')
        resp = platform.send_request(request)
        jsonObj = resp.json()
        print ("Fax sent. Message id: " + str(jsonObj.id))
        check_fax_message_status(jsonObj.id)
    except Exception as e:
        print (e)


# Check the sending message status until it's no longer in the queued status
def check_fax_message_status(messageId):
    try:
        endpoint = "/restapi/v1.0/account/~/extension/~/message-store/" + str(messageId)
        resp = platform.get(endpoint)
        jsonObj = resp.json()
        print ("Message status: " + jsonObj.messageStatus)
        if jsonObj.messageStatus == "Queued":
            time.sleep(10)
            check_fax_message_status(jsonObj.id)
    except Exception as e:
        print (e)

RECIPIENT = os.environ.get('RINGCENTRAL_RECEIVER')
# Authenticate a user using a personal JWT token
def login():
    try:
      platform.login( jwt=os.environ.get('RINGCENTRAL_JWT_TOKEN') )
      send_fax()
    except Exception as e:
      print ("Unable to authenticate to platform. Check credentials." + str(e))

# Instantiate the SDK and get the platform instance
rcsdk = SDK( os.environ.get('RINGCENTRAL_CLIENT_ID'),
             os.environ.get('RINGCENTRAL_CLIENT_SECRET'),
             os.environ.get('RINGCENTRAL_SERVER_URL') )
platform = rcsdk.platform()

login()

# For the purpose of testing the code, we put the recipient number in the variable.
# Feel free to set the recipient number directly.
