#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import argparse
import datetime

from slack import slack

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--payload", help = "A JSON payload containing all required data for the run. See payload class for details.")

args = parser.parse_args()

# Clean leading and trailing quotations
args.payload = args.payload[1:][:-1]


class Payload:

    # Incoming GHA Payload

    def __init__(self, raw):

        data = json.loads(raw)

        self.oauth = data["oauth"]
        self.status = data["status"]
        self.passed = ("success" == self.status)
        self.number = data["number"]
        self.image = data["image"]
        self.job = data["job"]


try:

    payload = Payload(raw = args.payload)

    if not (payload.passed and payload.number == 0):

        sender = slack.lookup_bot(oauth = payload.oauth)
        receiver = slack.lookup_channel(name = "autobuild-frontend")

        duration = datetime.timedelta(seconds = payload.seconds)

        passed = {
            True: {
                "icon": "https://i.imgur.com/iKI4cWZ.png",
                "keyword": "logging:success",
                "style": "primary",
                "emoji": "🚀"
            }, 
            False: {
                "icon": "https://i.imgur.com/qiIVN5S.png",
                "keyword": "logging:error",
                "style": "danger",
                "emoji": "💥"
            }
        }

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "Autobuild frontend completed an action",
                    "emoji": True
                }
            }, {
                "type": "context",
                "elements": [{
                    "type": "image",
                    "image_url": passed[payload.passed]["icon"],
                    "alt_text": "docker icon"
                }, {
                    "type": "mrkdwn",
                    "text": f"*keywords:* `{passed[payload.passed]['keyword']}`"     
                }]
            }, {
                "type": "actions",
                "elements": [{
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": passed[payload.passed]["emoji"] + "  View Action",
                        "emoji": True
                    },
                    "url": f"https://github.com/RemiMachina/RemiPlatform/actions/runs/{payload.job}",
                    "style": passed[payload.passed]["style"]
                }]
            }
        ]

        slack.send_blocks(blocks=blocks, sender=sender, receiver=receiver)

    else:

        print("No slack message sent")

except Exception as e:

    print(e)
    sys.exit(1)
