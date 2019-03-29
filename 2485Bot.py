import json
import os
from time import sleep
import sched
import time
import datetime
import multiprocessing
import copy
import calendar

from http.server import BaseHTTPRequestHandler, HTTPServer

from slackclient import SlackClient

from TheBlueAlliance import TBA

from oauth2client.service_account import ServiceAccountCredentials
import gspread

from sys import argv

EVENT = "2019nvlv"

TEAM = "frc2485"

lastMatchKey = ""
modifiedSince = 0

# sample sheet
SHEET_URL = 'https://docs.google.com/spreadsheets/d/1ahzHfDmDL5Id-toAyaCf5d1LAiDygfJPGKz1R1jrfRo/edit?ts=5c2c5962#gid' \
            '=1876596371 '

SHEET_NAME = "Calendar"
# it's REMIND TIME Y'ALL
REMIND_TIME = "18:00"
REMIND_DAYS_AHEAD = 2

# save TBA token as system variable 'TBA_API_TOKEN' and slack as 'SLACK_API_TOKEN'
SLACK_TOKEN = os.environ['SLACK_API_TOKEN']

sc = SlackClient(SLACK_TOKEN)

DEBUG_MODE = False

SHIFTS = {"Default": ["6pm-10pm"], "Saturday": ["8am-12pm", "12pm-5pm", "5pm-10pm"]}
SHIFTS_FORMAT = {}

for key, arr in SHIFTS.items():
    SHIFTS_FORMAT[key] = {}
    for index, value in enumerate(arr):
        SHIFTS_FORMAT[key][value] = []
PEOPLE_FORMAT = {"Design/Build": {}, "Soft/Strat": {}, "Bus/Out": {}, "Mentors": {}}
DEPARTMENT_HEADS = {"Design/Build": "Eleanor Hansen", "Soft/Strat": "Sahana Kumar", "Bus/Out": "Jake Brittain",
                    "Mentors": "Ryan Griggs", "Bot": "Nathan Sariowan"}


def post_message_to_slack(channel, message):
    print('Posting message to channel ' + channel + ' with text: ' + message)
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=message
    )


def get_all_slack_users():
    users = sc.api_call("users.list")
    if 'members' in users.keys():
        return sc.api_call("users.list")['members']
    else:
        print(users)


def do_invite(uid, channel):
    sc.api_call('channels.invite',
                channel=channel,
                user=uid,
                pretty=1)


def clear_b(text):
    if "<b>" in text:
        return clear_b(text[:text.index('<b>')] + text[text.index('<b>') + 3:])
    elif "</b>" in text:
        return clear_b(text[:text.index('</b>')] + text[text.index('</b>') + 4:])
    else:
        return text


def list_matches(data, request):
    ans = ""
    ans_list = []
    for item in data:
        ans_list.append(item[request])
    length = len(ans_list)
    ans_list.sort()
    for x in ans_list:
        index = ans_list.index(x)
        ans += str(x)
        if index == (length - 2):
            ans += ', and '
        elif index == (length - 1):
            ans += '.'
        else:
            ans += ', '
    return ans


def parse_command(post_data, command):
    return post_data[post_data.index('command=%2F') + 11:post_data.index('&text=')] == command


class S(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(b'<html><body><h1>hi!</h1></body></html>')

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data

        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        data = str(self.rfile.read(content_length))
        print(data)
        if "challenge" in data:
            challenge_token = data[data.index('challenge'):]
            self.wfile.write(bytes(challenge_token, 'utf-8'))
            return

        post_data = dict((k.strip(), v.strip()) for k, v in (item.split('=') for item in data.split('&')))
        print(post_data)
        self._set_headers()

        if "command" in post_data.keys():
            post_data["command"] = post_data["command"].replace("%2F", "")

        if "channel_created" in data:
            print('channel id!!! : ' + post_data["id"])
            sleep(1)
            do_invite('U0AK9DFK3', post_data["id"])
            self.wfile.write(200)


        elif post_data["command"] == 'rank':
            response = TBA.request("/team/frc2485/event/%s/status" % EVENT)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            data = json.loads(response.text)

            self.wfile.write(bytes(data["overall_status_str"].replace("<b>", "*").replace("</b>", "*"), 'utf-8'))
            # if "ranking" in data:
            #     self.wfile.write(b'Team 2485 is ranked ' + clear_b(data["ranking"]["rank"]))
            #     print('TBA RANKING: ' + data["ranking"]["rank"])
            # else:
            #     self.wfile.write(bytes(clear_b(data["overall_status_str"]), 'utf-8'))


        elif post_data["command"] == 'matches':
            response = TBA.request("/team/frc2485/event/%s/matches/simple" % EVENT)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            print(response.content)
            data = json.loads(response.text)
            if len(data) > 0:
                self.wfile.write(b'Team 2485 is in matches ')
                self.wfile.write(bytes(list_matches(data, "match_number"), 'utf-8'))
            else:
                self.wfile.write(b"Matches have not been posted yet.")
            print(data)

        elif post_data["command"] == 'lastmatch':
            response = TBA.request("/team/frc2485/event/%s/status" % EVENT)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            print(response.content)
            data = json.loads(response.text)
            if data["last_match_key"] is not None:
                matchkey = data["last_match_key"]
                matchdata = json.loads(TBA.request("/match/%s" % matchkey).text)

                winner = matchdata["winning_alliance"]

                ouralliance = ""
                otheralliance = ""

                if "frc2485" in matchdata["alliances"]["red"]["team_keys"]:
                    ouralliance = "red"
                    otheralliance = "blue"
                elif "frc2485" in matchdata["alliances"]["blue"]["team_keys"]:
                    ouralliance = "blue"
                    otheralliance = "red"

                wonlost = "won" if ouralliance == winner else "lost"

                string = "Team 2485's last match was match " + str(matchdata["match_number"])
                string += ". We *" + wonlost
                string += "* with score *" + str(matchdata["score_breakdown"][ouralliance]["totalPoints"]) + "-" + str(matchdata["score_breakdown"][otheralliance]["totalPoints"])
                string += " (" + str(matchdata["score_breakdown"][ouralliance]["rp"]) + " RP earned).* "
                string += data["overall_status_str"].replace("<b>", "").replace("</b>", "")

                self.wfile.write(bytes(string, "utf-8"))

            else:
                self.wfile.write(b"Team 2485 has not had any matches yet.")
            print(data)

        elif post_data["command"] == 'nextmatch':
            response = TBA.request("/team/frc2485/event/%s/status" % EVENT)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            print(response.content)
            data = json.loads(response.text)
            if data["next_match_key"] is not None:
                matchkey = data["next_match_key"]
                matchdata = json.loads(TBA.request("/match/%s" % matchkey).text)

                ouralliance = ""

                if "frc2485" in matchdata["alliances"]["red"]["team_keys"]:
                    ouralliance = "red"
                elif "frc2485" in matchdata["alliances"]["blue"]["team_keys"]:
                    ouralliance = "blue"

                time = datetime.datetime.fromtimestamp(int(matchdata["predicted_time"]))

                meridiem = "AM" if time.hour < 12 else "PM"

                hour = time.hour if time.hour < 12 else time.hour - 12
                


                alliances = matchdata["alliances"][ouralliance]["team_keys"]
                alliances.remove("frc2485")

                string = "Team 2485's next match is match *" + str(matchdata["match_number"])
                string += "* at *" + str(hour) + ":" + str(time.minute) + " " + meridiem + "*. "
                string += "Alliance partners: " + ", ".join(alliances).replace("frc", "") +  ". "

                self.wfile.write(bytes(string, "utf-8"))
            else:
                self.wfile.write(b"Match data has not been posted yet.")
            print(data)


        elif post_data["command"] == 'toggle-reminders':
            file = open("nosend.txt", "r")
            contents = file.read()
            contents_arr = contents.split(",")
            file.close()
            file = open("nosend.txt", "w")
            if post_data["user_id"] in contents_arr:
                contents = contents.replace("," + post_data["user_id"], "")
                self.wfile.write(b'You will now be sent reminders. Use \'/toggle-reminders\' to undo this.')
            else:
                contents += "," + post_data["user_id"]
                self.wfile.write(b'You will no longer be sent reminders. Use \'/toggle-reminders\' to undo this.')
            file.write(contents)
            file.close()


def get_sheet(url=SHEET_URL, sheet=SHEET_NAME):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_url(url)

    sheet = spreadsheet.worksheet(sheet)

    # Extract all of the values
    sheet_values = sheet.get_all_values()

    return sheet_values


def get_date(days_from_now=0):
    now = datetime.datetime.now()
    return str(now.month) + "/" + (str(now.day + days_from_now))


def get_day(days_from_now=0):
    now = datetime.datetime.now()
    return str(now.day + days_from_now)


def get_month_string(days_from_now=0):
    date = datetime.datetime.today() + datetime.timedelta(days=days_from_now)
    return calendar.day_name[date.weekday()] + ", " + date.strftime("%B") + " " + str(date.day)



def run_httpserver(port=8000, server_class=HTTPServer, handler_class=S):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever(poll_interval=0.5)


def run(port=8000):
    # http_thread = multiprocessing.Process(target=run_httpserver, args=(port,))
    #
    # http_thread.daemon = True
    #
    # if not DEBUG_MODE:
    #     http_thread.start()
    #
    # run_scheduler()

    run_httpserver(port)



if __name__ == "__main__":

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
