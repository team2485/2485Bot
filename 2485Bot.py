import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import requests
from slackclient import SlackClient

sc = SlackClient('xoxb-335481584838-ZaR0QmeauYp7aQfMVaZlvKj2')
sc.api_call(
  "chat.postMessage",
  channel="C9VB0E6ES",
  text="Hello from Python! :tada:"
)

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>hi!</h1></body></html>")

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        headers = {'X-TBA-Auth-Key': '69Ikp0hcU0yELOAOsk7cMVH8W1gQgKhtlk8NW6xYm2WDdtLEVZhrx65xCBBr54pd'}
        # Make a get request to get the latest position of the international space station from the opennotify api.
        response = requests.get("http://thebluealliance.com/api/v3/team/frc2485/event/2018nvlv/status", headers=headers)

        # Print the status code of the response.
        print('STATUS CODE: ' + str(response.status_code))
        data = json.loads(response.text)
        if "ranking" in data:
            self.wfile.write('Team 2485 is ranked ' + data["ranking"]["rank"])
        else:
            self.wfile.write(data["overall_status_str"])


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