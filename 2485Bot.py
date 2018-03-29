import json
import datetime
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from time import sleep
import requests
from slackclient import SlackClient


def doMessage(channel, message):
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

def getBlueAllianceResponse(request):
    headers = {'X-TBA-Auth-Key': '69Ikp0hcU0yELOAOsk7cMVH8W1gQgKhtlk8NW6xYm2WDdtLEVZhrx65xCBBr54pd'}
    print("URL ->>> " + ("http://thebluealliance.com/api/v3/team/frc2485%s" % request))
    return requests.get("http://thebluealliance.com/api/v3/team/frc2485%s" % request,
                            headers=headers)

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
        event = "nvlv";
        year = datetime.datetime.now().year
        event_key = str(year) + event
        print("YEAR ->>>>>>>>>>> " + event_key)
        self._set_headers()
        if "channel_created" in post_data:
            print('channel id!!! : ' + post_data[post_data.index('{"id":"') + 7:post_data.index('","is_channel"')])
            sleep(1)
            doMessage(post_data[post_data.index('{"id":"') + 7:post_data.index('","is_channel"')], 'FIRST!!1!')
            self.wfile.write(200)
        elif "channel_unarchive" in post_data:

            print('channel id!!! : ' + post_data[post_data.index(',"channel":') + 12:post_data.index('","user"')])
            doMessage(post_data[post_data.index(',"channel":') + 12:post_data.index('","user"')], 'FIRST!!1!')
            self.wfile.write(200)
        elif "challenge" in post_data:
            print(post_data[post_data.index("challenge") + 12:post_data.index("}") - 2])
            self.wfile.write(post_data[post_data.index("challenge") + 12:post_data.index("}") - 2])
        elif post_data[post_data.index('command=%2F') + 11:post_data.index('&text=')] == 'rank':
            response = getBlueAllianceResponse("/event/%s/status" % event_key)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            data = json.loads(response.text)
            print('TBA RETURN: ' + str(data))
            if "ranking" in data:
                self.wfile.write('Team 2485 is ranked ' + clear_b(data["ranking"]["rank"]))
                print('TBA RANKING: ' + data["ranking"]["rank"])
            else:
                self.wfile.write(clear_b(data["overall_status_str"]))
        elif post_data[post_data.index('command=%2F') + 11:post_data.index('&text=')] == 'matches':
            print('Matches!')
            response = getBlueAllianceResponse("/event/%s/matches/simple" % event_key)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            print(response.content)
            self.wfile.write('Team 2485 is in matches')
            data = json.loads(response.text)
            for i in range(len(data):
                 self.wfile.write(clear_b(data[i]["match_number"]))
            print(data[""])
        elif post_data[post_data.index('command=%2F') + 11:post_data.index('&text=')] == 'announcerank':
            response = getBlueAllianceResponse("/event/%s/status" % event_key)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            data = json.loads(response.text)
            print('TBA RETURN: ' + str(data))
            if "ranking" in data:
                self.wfile.write('Team 2485 is ranked ' + clear_b(data["ranking"]["rank"]))
                doMessage('C0A9JLBL2', 'Team 2485 is ranked ' + clear_b(data["ranking"]["rank"]))
            else:
                doMessage('C0A9JLBL2', clear_b(data["overall_status_str"]))
            self.wfile.write('Success!')
        elif post_data[post_data.index('command=%2F') + 11:post_data.index('&text=')] == 'init-cheer':
            doMessage('C0A9JLBL2', 'WE ARE...')
            self.wfile.write('Success!')
        elif post_data[post_data.index('command=%2F') + 11:post_data.index('&text=')] == 'cheer':
            doMessage('C0A9JLBL2', 'WARLORDS!')
            self.wfile.write('Success!')
        elif post_data[post_data.index('command=%2F') + 11:post_data.index('&text=')] == 'cheera':
            doMessage('C0A9JLBL2', 'WARLORDA!')
            self.wfile.write('Success!')


def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
