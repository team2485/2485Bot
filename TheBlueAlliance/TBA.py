import requests
import os


def request(request):
    headers = {'X-TBA-Auth-Key': os.environ['TBA_API_TOKEN']}
    print("URL ->>> " + ("http://thebluealliance.com/api/v3" + request))
    return requests.get("http://thebluealliance.com/api/v3" + request,
                        headers=headers)
