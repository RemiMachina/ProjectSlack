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

    # Required JSON format:
    # {
    #     "oauth": The secret oauth token of the bot to send the message
    #     "status": A flag indicating if the build passed and was successful
    #     "number": The number of files that were changed affecting this build. If 0 and passed, no message will be posted.
    #     "image": The display name of the docker image that has been built
    #     "seconds": The number of seconds taken by the build process
    #     "job": The id of the current github job - used for URL mapping
    #     "dockerhub": The full url of the dockerhub image
    # }

    def __init__(self, raw):

        print(raw)

        data = json.loads(raw)

        self.oauth = data["oauth"]
        self.status = data["status"]
        self.passed = ("success" == self.status)
        self.number = data["number"]
        self.image = data["image"]
        self.seconds = data["seconds"]
        self.job = data["job"]
        self.dockerhub = data["dockerhub"]


try:

    payload = Payload(raw = args.payload)

    if not (payload.passed and payload.number == 0):

        sender = slack.lookup_bot(oauth = payload.oauth)
        receiver = slack.lookup_channel(name = "github-actions")

        duration = datetime.timedelta(seconds = payload.seconds)

        passed = {
            True: {
                "icon": "https://i.imgur.com/iKI4cWZ.png",
                "message": f"*{payload.image}*: Build completed in {duration}",
                "style": "primary",
                "emoji": "🚀"
            }, 
            False: {
                "icon": "https://i.imgur.com/qiIVN5S.png",
                "message": f"*{payload.image}*: Build failed to complete in {duration}",
                "style": "danger",
                "emoji": "💥"
            }
        }

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "Github Actions has completed an image build",
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
                    "text": passed[payload.passed]["message"]
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
                    "url": f"https://github.com/RemiMachina/VNet/runs/{payload.job}",
                    "style": passed[payload.passed]["style"]
                }, {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🐋  Open Docker",
                        "emoji": True
                    },
                    "url": payload.dockerhub
                }]
            }
        ]

        slack.send_blocks(blocks = blocks, sender = sender, receiver = receiver)

    else:

        print("No slack message sent")

except Exception as e:

    print(e)
    sys.exit(1)