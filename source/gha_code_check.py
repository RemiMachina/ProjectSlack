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
    #     "lint": The path to the lint report
    #     "oauth": The oauth token of the sender
    # }

    def __init__(self, raw):

        print(raw)

        data = json.loads(raw)

        self.oauth = data["oauth"]
        self.run = data["run"]

        self.pylint_errors = data["pylint"]["errors"]
        self.pylint_warnings = data["pylint"]["warnings"]
        self.pylint_suggestions = data["pylint"]["suggestions"]
        
        self.pydoc_missing = data["pydoc"]["missing"]
        self.pydoc_conventions = data["pydoc"]["conventions"]

try:

    payload = Payload(raw = args.payload)

    sender = slack.lookup_bot(oauth = payload.oauth)
    receiver = slack.lookup_channel(name = "github-actions")

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "Python code check has completed",
                "emoji": True
            }
        }, {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Lint Report:* \n🚨  Errors: {payload.pylint_errors}\n⚠️  Warnings: {payload.pylint_warnings}\n💡  Sugestions: {payload.pylint_suggestions}\n"
            }
        }, {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Docstring Report:* \n🔍  Missing: {payload.pydoc_missing}\n👎  Conventions: {payload.pydoc_conventions}\n"
            }
        }, {
            "type": "actions",
            "elements": [{
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "🚀  View Action",
                    "emoji": True
                },
                "url": f"https://github.com/RemiMachina/VNet/runs/{payload.run}",
                "style": "primary"
            }]
        }
    ]

    slack.send_blocks(blocks = blocks, sender = sender, receiver = receiver)

except Exception as e:

    print(e)
    sys.exit(1)