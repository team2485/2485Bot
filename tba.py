import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import requests
from slackclient import SlackClient

class TBA():
    START_URL = "http://thebluealliance.com/api/v3/"

    def get(request):
        headers = {'X-TBA-Auth-Key': '69Ikp0hcU0yELOAOsk7cMVH8W1gQgKhtlk8NW6xYm2WDdtLEVZhrx65xCBBr54pd'}
        return requests.get(START_URL + request,
                                headers=headers)

    def getTeamRequest(request):
        return get("/team/frc2485/%s" % request)

    def getCommand(post_data, command):
        return post_data[post_data.index('command=%2F') + 11:post_data.index('&text=')] == command

    def getRank(event):
        return get("/event/%s/status" % event)

    def getMatches(event, simple=True):
        simpleString = "/simple" if simple else ""
        return get("/event/%s/matches%s" % event_key, simpleString)

    def toJSON(response):
        return json.loads(response.text)
