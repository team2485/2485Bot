import json
import datetime
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from time import sleep
from slackclient import SlackClient
from TheBlueAlliance import TBA
import MatchNotifier


def do_message(channel, message):
    sc = SlackClient('xoxb-335481584838-ZaR0QmeauYp7aQfMVaZlvKj2')
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

def list_entries(data, request):
    ans = ""
    length = len(data)
    for item in data:
        ans += str(item[request])
        index = data.index(item)

        if index == (length - 2):
            ans += ', and '
        elif index == (length - 1):
            ans += '.'
        else:
            ans += ", "
    return ans

def getCommand(post_data, command):
    return post_data[post_data.index('command=%2F') + 11:post_data.index('&text=')] == command

class S(BaseHTTPRequestHandler):
    CHANNEL_ID = 'C9X66KH5J' #champs-2018

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
        event = "gal"
        year = datetime.datetime.now().year
        event_key = str(year) + event
        print("YEAR ->>>>>>>>>>> " + event_key)
        self._set_headers()
        if "channel_created" in post_data:
            print('channel id!!! : ' + post_data[post_data.index('{"id":"') + 7:post_data.index('","is_channel"')])
            sleep(1)
            do_message(post_data[post_data.index('{"id":"') + 7:post_data.index('","is_channel"')], 'FIRST!!1!')
            self.wfile.write(200)
        elif "channel_unarchive" in post_data:

            print('channel id!!! : ' + post_data[post_data.index(',"channel":') + 12:post_data.index('","user"')])
            do_message(post_data[post_data.index(',"channel":') + 12:post_data.index('","user"')], 'FIRST!!1!')
            self.wfile.write(200)
        elif "challenge" in post_data:
            print(post_data[post_data.index("challenge") + 12:post_data.index("}") - 2])
            self.wfile.write(post_data[post_data.index("challenge") + 12:post_data.index("}") - 2])
        elif getCommand(post_data, 'rank'):
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
        elif getCommand(post_data, 'matches'):
            print('Matches!')
            response = TBA.request("/event/%s/matches/simple" % event_key)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            print(response.content)
            data = json.loads(response.text)

            if "match_number" in data:
                self.wfile.write('Team 2485 is in matches ')
                self.wfile.write(list_entries(data, "match_number"))
            else:
                self.wfile.write("Matches have not been posted yet.")
            print(data)
        elif getCommand(post_data, 'announcematches'):
            print('Matches!')
            response = TBA.request("/event/%s/matches/simple" % event_key)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            print(response.content)
            self.wfile.write('Team 2485 is in matches ')
            data = json.loads(response.text)
            do_message(CHANNEL_ID, list_entries(data, "match_number"))
            self.wfile.write('Success!')
            print(data)
        elif getCommand(post_data, 'announcerank'):
            response = TBA.request("/event/%s/status" % event_key)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            data = json.loads(response.text)
            print('TBA RETURN: ' + str(data))
            if "ranking" in data:
                self.wfile.write('Team 2485 is ranked ' + clear_b(data["ranking"]["rank"]))
                do_message(CHANNEL_ID, 'Team 2485 is ranked ' + clear_b(data["ranking"]["rank"]))
            else:
                do_message(CHANNEL_ID, clear_b(data["overall_status_str"]))
            self.wfile.write('Success!')
        elif getCommand(post_data, 'init-cheer'):
            do_message(CHANNEL_ID, 'WE ARE...')
            self.wfile.write('Success!')
        elif getCommand(post_data, 'cheer'):
            do_message(CHANNEL_ID, 'WARLORDS!')
            self.wfile.write('Success!')
        elif getCommand(post_data, 'cheera'):
            do_message(CHANNEL_ID, 'WARLORDA!')
            self.wfile.write('Success!')


def run(server_class=HTTPServer, handler_class=S, port=90):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    MatchNotifier.run()
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
