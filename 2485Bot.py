from slackclient import SlackClient

sc = SlackClient('xoxb-335481584838-ZaR0QmeauYp7aQfMVaZlvKj2')
sc.api_call(
  "chat.postMessage",
  channel="C9VB0E6ES",
  text="Hello from Python! :tada:"
)