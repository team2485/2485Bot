import json
import datetime
import time
import random
import os
import requests
from slackclient import SlackClient
from TheBlueAlliance import TBA

runNotifier = False

#webhook_url = "https://hooks.slack.com/services/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" #champs-2018
webhook_url = "https://hooks.slack.com/services/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" #houstonwehaveaproblem
#webhook_url = "https://hooks.slack.com/services/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" #rank
event_key = '2018gal'
#event_key = '2018casd'
phrases = ["Dylan, don't forget the battery.", "Good luck!", "We are WARLords!", "Warlorda!", "I need six eggs!", "Go :logo:!"]

def getTimestamp():
    return time.time()

def getNextMatch(data):
    for item in data.sort(key=extract_time, reverse=true):
        if item["predicted_time"] > getTimestamp() and "winning_alliance" not in item: #checks if match has already happened
            return data[item]

def extract_time(json):
    try:
        return json['predicted_time']
    except KeyError:
        return 0

def generateMessage(next_match):
    if 'frc2485' in next_match["alliances"]["blue"]["team_keys"]:
        alliance = "blue"
    else:
        alliance = "red"
    output = "Coming up: Team 2485 will be in match " + str(next_match["match_number"]) + " on the " + alliance + " alliance. "
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

def getRunNotifier():
    return runNotifier

def setRunNotifier(set):
    print("runNotifier set to " + str(set))
    runNotifier = set

def run():
    print('success!')
    while(True): #YOU HAVE TO FIX THIS BECAUSE THIS IS A BAD, BAD WAY OF DOING THINGS
	print(getTimeStamp())
	if (getRunNotifier()):
            response = TBA.request("/event/%s/matches/simple" % event_key)
            data = json.loads(response.text)
            next_match = getNextMatch(data)
            if next_match is not None and getTimestamp() > next_match["predicted_time"] - 300 and getTimestamp() < next_match["predicted_time"] - 200:
                postMessage(generateMessage(next_match))
                time.sleep(100)
	time.sleep(1)
