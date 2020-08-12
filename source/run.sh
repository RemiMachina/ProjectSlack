#!/bin/sh -l

echo "Hello"
python /source/$SLACK_SCRIPT.py --payload "'$SLACK_PAYLOAD'"
echo "Goodbye"