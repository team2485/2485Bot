import json
import os
from time import sleep
import schedule
import time
import multiprocessing

from http.server import BaseHTTPRequestHandler, HTTPServer

from slackclient import SlackClient

from TheBlueAlliance import TBA

import oauth2client
from oauth2client.service_account import ServiceAccountCredentials
import gspread

from sys import argv

spreadsheet_name = "Sample Sheet"

sheet_name = "sheet1"

slack_token = os.environ['SLACK_TOKEN']


sc = SlackClient(slack_token)

remind_time = "18:00"

def post_message(channel, message):
    print('Posting message to channel ' + channel + ' with text: ' + message)
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=message
    )

def clear_b(input):
    if "<b>" in input:
        return clear_b(input[:input.index('<b>')] + input[input.index('<b>') + 3:])
    elif "</b>" in input:
        return clear_b(input[:input.index('</b>')] + input[input.index('</b>') + 4:])
    else:
        return input


def list_matches(data, request):
    ans = ""
    ansList = []
    for item in data:
        ansList.append(item[request])
    length = len(ansList)
    ansList.sort()
    for x in ansList:
        index = ansList.index(x)
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
        CHANNEL_ID = post_data[post_data.index('&channel_id=') + 12:post_data.index('&channel_name=')]
        text = post_data[post_data.index('&text=') + 6:post_data.index('&response_url=')]
        if "channel_created" in post_data:
            print('channel id!!! : ' + post_data[post_data.index('{"id":"') + 7:post_data.index('","is_channel"')])
            sleep(1)
            post_message(post_data[post_data.index('{"id":"') + 7:post_data.index('","is_channel"')], 'FIRST!!1!')
            self.wfile.write(200)
        elif "channel_unarchive" in post_data:

            print('channel id!!! : ' + post_data[post_data.index(',"channel":') + 12:post_data.index('","user"')])
            post_message(post_data[post_data.index(',"channel":') + 12:post_data.index('","user"')], 'FIRST!!1!')
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
                post_message(CHANNEL_ID, list_matches(data, "match_number"))
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
                post_message(CHANNEL_ID, 'Team 2485 is ranked ' + clear_b(data["ranking"]["rank"]))
            else:
                post_message(CHANNEL_ID, clear_b(data["overall_status_str"]))
            self.wfile.write('Success!')
        elif parse_command(post_data, 'init-cheer'):
            post_message(CHANNEL_ID, 'WE ARE...')
            self.wfile.write('Success!')
        elif parse_command(post_data, 'cheer'):
            post_message(CHANNEL_ID, 'WARLORDS!')
            self.wfile.write('Success!')
        elif parse_command(post_data, 'cheera'):
            post_message(CHANNEL_ID, 'WARLORDA!')
            self.wfile.write('Success!')


def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1oChCUMXV777wrI3ixMhWpksKlqQd2co0U5gqvMa2nGI/edit#gid=0')

    sheet = spreadsheet.sheet1

    # Extract and print all of the values
    list_of_hashes = sheet.get_all_records()
    print(list_of_hashes)

    return list_of_hashes

def send_reminder():
    get_sheet()


def run_scheduler():
    send_reminder()

    # schedule.every().day.at(remind_time).do(send_reminder)

    poll_scheduler()

def poll_scheduler():
    schedule.run_pending()
    time.sleep(1)
    poll_scheduler()

def run_httpserver(port=90, server_class=HTTPServer, handler_class=S):

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever(poll_interval=0.5)


def run(port=90):

    # scheduler_thread = multiprocessing.Process(target=run_scheduler, args=())

    http_thread = multiprocessing.Process(target=run_httpserver, args=(port,))

    #idk  why this works but eh
    http_thread.daemon = True

    http_thread.start()

    run_scheduler()


if __name__ == "__main__":

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

