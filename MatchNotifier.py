import json
import datetime
import time
import random
import os
import requests
from slackclient import SlackClient
from TheBlueAlliance import TBA



#webhook_url = "https://hooks.slack.com/services/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"
webhook_url = "https://hooks.slack.com/services/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"
#event_key = '2018gal'
event_key = '2018casd'
phrases = ["Dylan, don't forget the battery.", "Good luck!", "We are WARLords!", "Warlorda!", "I need six eggs!", "Go :logo:!"]

def getTimestamp():
    return time.time()

def getNextMatch(data):
    return data[0]
    for item in data:
        if item["predicted_time"] > getTimestamp() and "winning_alliance" not in item: #checks if match has already happened
            return data[item]


def generateMessage(next_match):
    if 'frc2485' in next_match["alliances"]["blue"]["team_keys"]:
        alliance = "blue"
    else:
        alliance = "red"
    output = "Team 2485 will be in match " + str(next_match["match_number"]) + " soon on the " + alliance + " alliance. "
    output += phrases[random.randint(0, len(phrases)-1)]
    print output
    return output

def postMessage(main):
    url = webhook_url
    payload = {
        'text': main
    }

    r = requests.post(url, data=json.dumps(payload))
    status_code = r.status_code

# Check the status code of the respond you receive from Slack.
# If it's an error, flash a message about it at the bottom of the page.
    if status_code == 200:
        print('Webhook succeeded with status code 200')
    else:
        print('Webhook failed with status code error %s.' % (status_code))

def run():
    response = TBA.request("/event/%s/matches/simple" % event_key)
    data = json.loads(response.text)
    next_match = getNextMatch(data)
    if next_match is not None and getTimestamp > (next_match["predicted_time"] - 300):
        postMessage(generateMessage(next_match))
