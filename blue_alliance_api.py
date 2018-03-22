from pip._vendor import requests


def main():
    headers = {'X-TBA-Auth-Key': '69Ikp0hcU0yELOAOsk7cMVH8W1gQgKhtlk8NW6xYm2WDdtLEVZhrx65xCBBr54pd'}
    # Make a get request to get the latest position of the international space station from the opennotify api.
    response = requests.get("http://thebluealliance.com/api/v3/team/frc2485/matches/2017/simple", headers=headers)

    # Print the status code of the response.
    print(response.status_code)
    print(response.content)


if __name__ == '__main__':
    main()
