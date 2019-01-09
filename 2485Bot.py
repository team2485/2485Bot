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

# SHIFTS_FORMAT = {"Default": {"6pm-10pm": []}, "Saturday": {"8am-12pm": [], "12pm-5pm": [], "5pm-10pm": []}}

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
        if "challenge" in data:
            print("uwu i got a challenge goku-san, i'll complete it well~! here have its contents")
            print(data)
            self.wfile.write(bytes(data['challenge'], 'utf-8'))
            return
        post_data = dict((k.strip(), v.strip()) for k, v in (item.split('=') for item in data.split('&')))
        print(post_data)
        event_key = "2018gal"
        print("YEAR ->>>>>>>>>>> " + event_key)
        self._set_headers()

        if "command" in post_data.keys():
            post_data["command"] = post_data["command"].replace("%2F", "")

        if "channel_created" in data:
            print('channel id!!! : ' + post_data["id"])
            sleep(1)
            do_invite('U0AK9DFK3', post_data["id"])
            self.wfile.write(200)
        elif "channel_unarchive" in data:
            do_invite('U0AK9DFK3', post_data["id"])
            print('channel id!!! : ' + post_data["id"])
            self.wfile.write(200)
        elif post_data["command"] == 'rank':
            response = TBA.request("/event/%s/status" % event_key)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            data = json.loads(response.text)
            print('TBA RETURN: ' + str(data))
            if "ranking" in data:
                self.wfile.write(b'Team 2485 is ranked ' + clear_b(data["ranking"]["rank"]))
                print('TBA RANKING: ' + data["ranking"]["rank"])
            else:
                self.wfile.write(bytes(clear_b(data["overall_status_str"]), 'utf-8'))
        elif post_data["command"] == 'matches':
            print('Matches!')
            response = TBA.request("/event/%s/matches/simple" % event_key)
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
        elif post_data["command"] == 'announcematches':
            print('Matches!')
            response = TBA.request("/event/%s/matches/simple" % event_key)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            print(response.content)
            self.wfile.write(b'Team 2485 is in matches ')
            data = json.loads(response.text)
            if len(data) > 0:
                post_message_to_slack(post_data['channel_id'], list_matches(data, "match_number"))
                self.wfile.write(b'Success!')
            else:
                self.wfile.write(b"Matches have not been posted yet.")
            print(data)
        elif post_data["command"] == 'announcerank':
            response = TBA.request("/event/%s/status" % event_key)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            data = json.loads(response.text)
            print('TBA RETURN: ' + str(data))
            if "ranking" in data:
                self.wfile.write(b'Team 2485 is ranked ' + clear_b(data["ranking"]["rank"]))
                post_message_to_slack(post_data['channel_id'],
                                      'Team 2485 is ranked ' + clear_b(data["ranking"]["rank"]))
            else:
                post_message_to_slack(post_data['channel_id'], clear_b(data["overall_status_str"]))
            self.wfile.write(b'Success!')
        elif post_data["command"] == 'init-cheer':
            post_message_to_slack(post_data['channel_id'], 'WE ARE...')
            self.wfile.write(b'Success!')
        elif post_data["command"] == 'cheer':
            post_message_to_slack(post_data['channel_id'], 'WARLORDS!')
            self.wfile.write(b'Success!')
        elif post_data["command"] == 'cheera':
            post_message_to_slack(post_data['channel_id'], 'WARLORDA!')
            self.wfile.write(b'Success!')
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


def get_people_from_sheet(date, sheet=SHEET_NAME):
    sheet_values = get_sheet(sheet=sheet)

    # date_cols is a list as some days (ie Saturdays) have multiple shifts listed on the same row.
    date_cols = []
    date_row = -1

    day_key = "Default"

    people = PEOPLE_FORMAT.copy()

    # find location of date
    for row, arr in enumerate(sheet_values):
        for col, val in enumerate(arr):
            nums = [int(s) for s in val.split() if s.isdigit()]
            if len(nums) > 0 and date == str(nums[0]):
                date_cols.append(col)
                date_row = row

        # breaks here to allow adding other shifts on the same day
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

                vals = val.split(', ')
                final_vals = []

                for person in vals:
                    if person not in final_vals:
                        final_vals.append(person)

                if department in people.keys():
                    people[department][shift_key] += final_vals

                name_row += 1

        shift += 1

    return people


def send_reminders():
    day = get_day(REMIND_DAYS_AHEAD)

    people = get_people_from_sheet(date=day)

    print("People to remind:", people)

    slack_users = get_all_slack_users()

    user_ids = {}

    missing_people = []

    for department, dict in people.items():
        for shift, arr in dict.items():
            for name in arr:
                if name not in missing_people:
                    missing_people.append(name)

    found_persons = []

    for user in slack_users:
        name = user["profile"]["real_name_normalized"]
        for person in missing_people:

            same_person = True

            name_arr = name.split(" ")
            person_arr = person.split(" ")

            for person_part in person_arr:
                if person_part not in name_arr:
                    same_person = False
                    break

            if same_person:
                if person in found_persons:
                    found_persons.remove(person)
                    user_ids[person] = ''
                    missing_people.append(person + " (multiple found)")
                elif len(person) > 0:
                    found_persons.append(person)
                    user_ids[person] = user["id"]
                    if person in missing_people:
                        missing_people = list(filter(lambda a: a != person, missing_people))

        for key, value in DEPARTMENT_HEADS.items():
            if name == value:
                DEPARTMENT_HEADS[key] = user["id"]

    # todo deal with non saturdays

    debug_string = "Sent to: "

    file = open("nosend.txt", "r")
    contents = file.read()
    no_send = contents.split(",")

    print("No send:", no_send)

    for department, dict in people.items():
        for shift, arr in dict.items():
            for name in arr:
                if name not in missing_people and name in list(user_ids.keys()) and user_ids[name] not in no_send:
                    string = "Hello " + "<@" + user_ids[name] + ">" + ", "
                    string += "you are signed up " + str(REMIND_DAYS_AHEAD) + " days from now "
                    string += "on *" + get_month_string(REMIND_DAYS_AHEAD) + "* "
                    string += "for the *" + shift + "* shift. "
                    string += "\nIf you need to reschedule, please dm " + "<@" + DEPARTMENT_HEADS[
                        department] + ">" + ". "
                    string += "To opt out of reminders, type \'/toggle-reminders\'. "
                    string += "<" + SHEET_URL + "|Click here to go to the Scheduling Sheet.>"

                    print(string)

                    debug_string += "<@" + user_ids[name] + "> "

                    if not DEBUG_MODE:
                        post_message_to_slack(user_ids[name], string)

    debug_string += "\nNot Found: "

    for value in missing_people:
        debug_string += value + " "

    print(debug_string)

    post_message_to_slack((DEPARTMENT_HEADS["Bot"]), debug_string)


def poll_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


def run_scheduler():
    if not DEBUG_MODE:
        print("Running scheduler...")
        schedule.every().day.at(REMIND_TIME).do(send_reminders)
    else:
        print("Sending message...")
        send_reminders()

    poll_scheduler()


def run_httpserver(port=8000, server_class=HTTPServer, handler_class=S):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever(poll_interval=0.5)


def run(port=8000):
    http_thread = multiprocessing.Process(target=run_httpserver, args=(port,))

    # idk  why this works but eh
    http_thread.daemon = True

    if not DEBUG_MODE:
        http_thread.start()

    run_scheduler()


if __name__ == "__main__":

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
