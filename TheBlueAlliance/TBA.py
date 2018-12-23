import requests
import os


def request(request):
    headers = {'X-TBA-Auth-Key': os.environ['2485BOT_TBA_API_TOKEN']}
    print("URL ->>> " + ("http://thebluealliance.com/api/v3/team/frc2485%s" % request))
    return requests.get("http://thebluealliance.com/api/v3/team/frc2485%s" % request,
                        headers=headers)
