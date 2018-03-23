import json

from pip._vendor import requests


def main():
    headers = {'X-TBA-Auth-Key': '69Ikp0hcU0yELOAOsk7cMVH8W1gQgKhtlk8NW6xYm2WDdtLEVZhrx65xCBBr54pd'}
    # Make a get request to get the latest position of the international space station from the opennotify api.
    response = requests.get("http://thebluealliance.com/api/v3/team/frc2485/event/2018nvlv/status", headers=headers)

    # Print the status code of the response.
    print('STATUS CODE: ' + str(response.status_code))
    print(response.content)
    data = json.loads(response.text)
    print(data["overall_status_str"])


if __name__ == '__main__':
    main()
