import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

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
        if "channel_created" in post_data:
            self._set_headers()
            print('channel id!!! : ' + post_data[post_data.index('{"id":"') + 7:post_data.index('","user"')])
            doMessage(post_data[post_data.index('{"id":"') + 7:post_data.index('","user"')], 'FIRST!!1!')
            self.wfile.write(200)
        elif "channel_unarchive" in post_data:
            self._set_headers()
            print('channel id!!! : ' + post_data[post_data.index(',"channel":') + 12:post_data.index('","user"')])
            doMessage(post_data[post_data.index(',"channel":') + 12:post_data.index('","user"')], 'FIRST!!1!')
            self.wfile.write(200)
        elif "challenge" in post_data:
            self._set_headers()
            print(post_data[post_data.index("challenge") + 12:post_data.index("}") - 2])
            self.wfile.write(post_data[post_data.index("challenge") + 12:post_data.index("}") - 2])
        elif post_data[post_data.index('command=%2F') + 11:post_data.index('&text=')] == 'rank':
            self._set_headers()
            headers = {'X-TBA-Auth-Key': '69Ikp0hcU0yELOAOsk7cMVH8W1gQgKhtlk8NW6xYm2WDdtLEVZhrx65xCBBr54pd'}
            # Make a get request to get the latest position of the international space station from the opennotify api.
            response = requests.get("http://thebluealliance.com/api/v3/team/frc2485/event/2018nvlv/status",
                                    headers=headers)

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
            self._set_headers()
            print('Matches!')
            headers = {'X-TBA-Auth-Key': '69Ikp0hcU0yELOAOsk7cMVH8W1gQgKhtlk8NW6xYm2WDdtLEVZhrx65xCBBr54pd'}
            # Make a get request to get the latest position of the international space station from the opennotify api.
            response = requests.get("http://thebluealliance.com/api/v3/team/frc2485/event/2018nvlv/matches",
                                    headers=headers)
            # Print the status code of the response.
            print('STATUS CODE: ' + str(response.status_code))
            print(response.content)
            data = json.loads(response.text)
            print(data[""])


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
