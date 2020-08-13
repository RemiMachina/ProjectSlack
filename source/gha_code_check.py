#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

        self.lint = data["lint"]
        self.oauth = data["oauth"]

try:

    payload = Payload(raw = args.payload)

    sender = slack.lookup_bot(oauth = payload.oauth)
    receiver = slack.lookup_channel(name = "github-actions")

    slack.send_file(path = payload.lint, sender = sender, receiver = receiver)

except Exception as e:

    print(e)