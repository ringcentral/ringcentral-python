#!/usr/bin/env python
# encoding: utf-8

import urllib
from config import USERNAME, EXTENSION, PASSWORD, APP_KEY, APP_SECRET, SERVER, MOBILE
from ringcentral import SDK


def main():
    sdk = SDK(APP_KEY, APP_SECRET, SERVER)
    platform = sdk.platform()
    platform.login(USERNAME, EXTENSION, PASSWORD)

    # Step 1. Get an answering rule ID

    answering_rules = platform.get('/account/~/extension/~/answering-rule').json().records
    last_answer_rule_id = answering_rules[-1].id
    print 'Answering rule ID: ' + last_answer_rule_id

    # Step 2. Update greeting audio file

    binary = (
        'test.mp3',
        urllib.urlopen('https://freesound.org/data/previews/85/85785_14771-lq.mp3').read(),
        'audio/mpeg'
    )
    builder = sdk.create_multipart_builder()
    builder.set_body({
        'type': 'Voicemail',
        'answeringRule': { 'id': last_answer_rule_id }
    })
    builder.add(binary)
    builder.set_multipart_mixed(True)
    request = builder.request('/account/~/extension/~/greeting')
    response = platform.send_request(request)
    print 'Updated greeting audio: ' + response.json().uri


if __name__ == '__main__':
    main()