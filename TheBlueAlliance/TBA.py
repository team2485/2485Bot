import requests


def request(request):
    headers = {'X-TBA-Auth-Key': '69Ikp0hcU0yELOAOsk7cMVH8W1gQgKhtlk8NW6xYm2WDdtLEVZhrx65xCBBr54pd'}
    print("URL ->>> " + ("http://thebluealliance.com/api/v3/team/frc2485%s" % request))
    return requests.get("http://thebluealliance.com/api/v3/team/frc2485%s" % request,
                        headers=headers)
