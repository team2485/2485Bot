import json
import os
from time import sleep
import schedule
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

#sample sheet
SHEET_URL = 'https://docs.google.com/spreadsheets/d/1ahzHfDmDL5Id-toAyaCf5d1LAiDygfJPGKz1R1jrfRo/edit?ts=5c2c5962#gid=1876596371'

SHEET_NAME = "Calendar"

# it's REMIND TIME Y'ALL
REMIND_TIME = "18:00"

REMIND_DAYS_AHEAD = 2

#save TBA token as system variable 'TBA_API_TOKEN' and slack as 'SLACK_API_TOKEN'
SLACK_TOKEN = os.environ['SLACK_API_TOKEN']

sc = SlackClient(SLACK_TOKEN)

DEBUG_MODE = False

SHIFTS = {"Default": ["6pm-10pm"], "Saturday": ["8am-12pm", "12pm-5pm", "5pm-10pm"]}

# SHIFTS_FORMAT = {"Default": {"6pm-10pm": []}, "Saturday": {"8am-12pm": [], "12pm-5pm": [], "5pm-10pm": []}}

SHIFTS_FORMAT = {}

for key, arr in SHIFTS.items():
    SHIFTS_FORMAT[key] = {}

    for index, value in enumerate(arr):
        SHIFTS_FORMAT[key][value] = []

PEOPLE_FORMAT = {"Design/Build": {}, "Soft/Strat": {}, "Bus/Out": {}};

DEPARTMENT_HEADS = {"Design/Build": "Eleanor Hansen", "Soft/Strat": "Sahana Kumar", "Bus/Out": "Jake Brittain", "Bot": "Nathan Sariowan"}

def post_message_to_slack(channel, message):
    print('Posting message to channel ' + channel + ' with text: ' + message)
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=message
    )

def get_all_slack_users():
    return sc.api_call("users.list")['members']

def do_invite(uid, channel):
    sc.api_call('channels.invite',
                channel=channel,
                user=uid,
                pretty=1)


def clear_b(input):
    if "<b>" in input:
        return clear_b(input[:input.index('<b>')] + input[input.index('<b>') + 3:])
    elif "</b>" in input:
        return clear_b(input[:input.index('</b>')] + input[input.index('</b>') + 4:])
    else:
        return input


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
        self.wfile.write('<html><body><h1>hi!</h1></body></html>')

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data

        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        print(post_data)
        event_key = "2018gal"
        print("YEAR ->>>>>>>>>>> " + event_key)
        self._set_headers()
        channel_id = post_data[post_data.index('&channel_id=') + 12:post_data.index('&channel_name=')]
        text = post_data[post_data.index('&text=') + 6:post_data.index('&response_url=')]
        if "channel_created" in post_data:
            print('channel id!!! : ' + post_data[post_data.index('{"id":"') + 7:post_data.index('","is_channel"')])
            sleep(1)
            do_invite('U0AK9DFK3', post_data[post_data.index('{"id":"') + 7:post_data.index('","is_channel"')])
            self.wfile.write(200)
        elif "channel_unarchive" in post_data:
            do_invite('U0AK9DFK3', post_data[post_data.index('{"id":"') + 7:post_data.index('","is_channel"')])
            print('channel id!!! : ' + post_data[post_data.index(',"channel":') + 12:post_data.index('","user"')])
            self.wfile.write(200)
        elif "challenge" in post_data:
            print(post_data[post_data.index("challenge") + 12:post_data.index("}") - 2])
            self.wfile.write(post_data[post_data.index("challenge") + 12:post_data.index("}") - 2])
        elif parse_command(post_data, 'rank'):
            response = TBA.request("/event/%s/status" % event_key)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            data = json.loads(response.text)
            print('TBA RETURN: ' + str(data))
            if "ranking" in data:
                self.wfile.write('Team 2485 is ranked ' + clear_b(data["ranking"]["rank"]))
                print('TBA RANKING: ' + data["ranking"]["rank"])
            else:
                self.wfile.write(clear_b(data["overall_status_str"]))
        elif parse_command(post_data, 'matches'):
            print('Matches!')
            response = TBA.request("/event/%s/matches/simple" % event_key)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            print(response.content)
            data = json.loads(response.text)
            if len(data) > 0:
                self.wfile.write('Team 2485 is in matches ')
                self.wfile.write(list_matches(data, "match_number"))
            else:
                self.wfile.write("Matches have not been posted yet.")
            print(data)
        elif parse_command(post_data, 'announcematches'):
            print('Matches!')
            response = TBA.request("/event/%s/matches/simple" % event_key)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            print(response.content)
            self.wfile.write('Team 2485 is in matches ')
            data = json.loads(response.text)
            if len(data) > 0:
                post_message_to_slack(channel_id, list_matches(data, "match_number"))
                self.wfile.write('Success!')
            else:
                self.wfile.write("Matches have not been posted yet.")
            print(data)
        elif parse_command(post_data, 'announcerank'):
            response = TBA.request("/event/%s/status" % event_key)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            data = json.loads(response.text)
            print('TBA RETURN: ' + str(data))
            if "ranking" in data:
                self.wfile.write('Team 2485 is ranked ' + clear_b(data["ranking"]["rank"]))
                post_message_to_slack(channel_id, 'Team 2485 is ranked ' + clear_b(data["ranking"]["rank"]))
            else:
                post_message_to_slack(channel_id, clear_b(data["overall_status_str"]))
            self.wfile.write('Success!')
        elif parse_command(post_data, 'init-cheer'):
            post_message_to_slack(channel_id, 'WE ARE...')
            self.wfile.write('Success!')
        elif parse_command(post_data, 'cheer'):
            post_message_to_slack(channel_id, 'WARLORDS!')
            self.wfile.write('Success!')
        elif parse_command(post_data, 'cheera'):
            post_message_to_slack(channel_id, 'WARLORDA!')
            self.wfile.write('Success!')


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

def get_people_from_sheet(date, sheet=SHEET_NAME):
    sheet_values = get_sheet(sheet=sheet)

    #date_cols is a list as some days (ie Saturdays) have multiple shifts listed on the same row.
    date_cols = []
    date_row = -1

    day_key = "Default"

    people = PEOPLE_FORMAT.copy()

    # find location of date
    for row, arr in enumerate(sheet_values):
        for col, val in enumerate(arr):
            if date in val:
                date_cols.append(col)
                date_row = row

        #breaks here to allow adding other shifts on the same day
        if date_row > -1:
            break

    # find what day it is
    for key, value in SHIFTS_FORMAT.items():
        for row, arr in enumerate(sheet_values):
            if key in arr[date_cols[0]]:
                day_key = key

    # prep shifts
    for key, value in people.items():
        # DEEP copy (.copy() method doesn't work for some reason)
        people[key] = copy.deepcopy(SHIFTS_FORMAT[day_key])

    shift = 0

    # get people
    for col in date_cols:
        is_a_name = True
        name_row = date_row + 1

        shift_key = SHIFTS[day_key][shift]

        while is_a_name and name_row < len(sheet_values):
            val = sheet_values[name_row][col]
            department = sheet_values[name_row][0]

            if any(char.isdigit() for char in val):
                is_a_name = False
            else:
                people[department][shift_key] += val.split(', ')
                name_row += 1


        shift+=1

    return people

def send_reminders():

    day = get_day(REMIND_DAYS_AHEAD)

    people = get_people_from_sheet(date=day)

    print("People to remind:", people)

    slack_users = get_all_slack_users()

    user_ids = {}

    missing_people = []

    for department, dict in people.items():
        for shift, name in dict.items():
            missing_people += name

    for user in slack_users:
        name = user["profile"]["real_name_normalized"]
        if name in missing_people:
            user_ids[name] = user["id"]
            missing_people.remove(name)
        for key, value in DEPARTMENT_HEADS.items():
            if name == value:
                DEPARTMENT_HEADS[key] = user["id"]

    if len(people) > 0:
        print("Not found: ", missing_people)

# todo deal with non saturdays

    debug_string = "Sent to: "

    for department, dict in people.items():
        for shift, arr in dict.items():
            for name in arr:
                if name not in missing_people and name in list(user_ids.keys()):
                    string = "Hello " + "<@" + user_ids[name] + ">" + ", "
                    string += "you are signed up " + str(REMIND_DAYS_AHEAD) + " days from now "
                    string += "on *" + get_month_string(REMIND_DAYS_AHEAD)  + "* "
                    string += "for the *" + shift + "* shift. "
                    string += "If you need to reschedule, please dm " + "<@" + DEPARTMENT_HEADS[department] + ">" + "."

                    print(string)

                    debug_string += "<@" + user_ids[name] + "> "

                    if not DEBUG_MODE:
                        post_message_to_slack(user_ids[name], string)

    debug_string += "\nNot Found: "

    for value in missing_people:
        debug_string += value + " "

    post_message_to_slack((DEPARTMENT_HEADS["bot"]), debug_string)



def poll_scheduler():
    schedule.run_pending()
    time.sleep(1)
    #recursive loop because recursive loops are fun
    poll_scheduler()

def run_scheduler():

    if not DEBUG_MODE:
        print("Running scheduler...")
        schedule.every().day.at(REMIND_TIME).do(send_reminders)
    else:
        print("Sending message...")
        send_reminders()

    poll_scheduler()

def run_httpserver(port=90, server_class=HTTPServer, handler_class=S):

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever(poll_interval=0.5)


def run(port=90):

    http_thread = multiprocessing.Process(target=run_httpserver, args=(port,))

    #idk  why this works but eh
    http_thread.daemon = True

    if not DEBUG_MODE:
        http_thread.start()

    run_scheduler()


if __name__ == "__main__":

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

