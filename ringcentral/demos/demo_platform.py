from ringcentral import SDK
from dotenv import dotenv_values, find_dotenv

env = dotenv_values(find_dotenv())

def create_delete_bridge(platform):
    body = {
        "name": "Weekly Meeting with Sushil",
        "type": "Instant",
        "security": {
            "passwordProtected": True,
            "password": "Wq123ygs15",
            "noGuests": False,
            "sameAccount": False,
            "e2ee": False
        },
        "preferences": {
            "join": {
                "audioMuted": False,
                "videoMuted": False,
                "waitingRoomRequired": "Nobody",
                "pstn": {
                    "promptAnnouncement": True,
                    "promptParticipants": True
                }
            },
            "playTones": "Off",
            "musicOnHold": True,
            "joinBeforeHost": True,
            "screenSharing": True,
            "recordingsMode": "User",
            "transcriptionsMode": "User",
            "recordings": {
                "everyoneCanControl": {
                    "enabled": True
                },
                "autoShared": {
                    "enabled": True
                }
            },
            "allowEveryoneTranscribeMeetings": True
        }
    }
    create_respone = platform.post(url='/rcvideo/v2/account/~/extension/~/bridges', body=body)
    print("Id = "+create_respone.json().id)
    print("Meeting Name = "+create_respone.json().name)
    platform.delete(url="/rcvideo/v2/bridges/" + str(create_respone.json().id))

def main():
    sdk = SDK(env['RINGCENTRAL_CLIENT_ID'], env['RINGCENTRAL_CLIENT_SECRET'], env['RINGCENTRAL_SERVER_URL'])
    platform = sdk.platform()
    platform.login(jwt = env['RINGCENTRAL_JWT_TOKEN'])
    create_delete_bridge(platform)
if __name__ == '__main__':
    main()