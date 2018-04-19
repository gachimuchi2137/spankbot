import os
import time
import re
from slackclient import SlackClient
from math import sqrt
import random
import requests


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
yt_api_key = os.environ.get('YT_API_KEY')
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
YT_VIDS = []

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def random_video():
    r = requests.get('https://www.googleapis.com/youtube/v3/search?part=id&maxResults=50&type=video&q=gachi&key={}'.format(yt_api_key))
    r = r.json()
    for item in r['items']:
        YT_VIDS.append(item['id']['videoId'])
    r = requests.get('https://www.googleapis.com/youtube/v3/search?part=id&maxResults=50&type=video&q=right+version&key={}'.format(yt_api_key))
    r = r.json()
    for item in r['items']:
        YT_VIDS.append(item['id']['videoId'])

def random_videoid():
    return random.choice(YT_VIDS)

def get_yt_link():
    return "https://youtube.com/watch?v=" + random_videoid()
        

def fibo(command):
    digit = ''.join(c for c in command if c.isdigit())
    if digit == '':
        return "GTFO MOTHER FUCKER XD"
    n = int(digit)
    try:
        a = ((1+sqrt(5))**n-(1-sqrt(5))**n)/(2**n*sqrt(5))
        return a
    except Exception as e:
        return "Fuck youuu {} {}".format(e.__class__.__name__, e.message)

def handle_command(command, channel, slack_id):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Kurwa jeszcze nie ogarniam za duzo ..."

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"

    if command.startswith("spank"):
        response = "Oh... It turns me on"

    if command == "Who are you?":
        response = "I'm an artist. A performace artist. :gsanta:"

    if command == "How much is anal fisting?":
        response = "Fisting is 300$"
    
    if command == "anal":
        response = "I don't do anal. Dont' touch me there."

    if command.startswith("fibo"):
        calc = fibo(command)
        response = "I guess it's {} aaahhhhh".format(calc)

    if command == 'music':
        link = random.choice(YT_VIDS)
        response = link
    if command == 'vid':
        link = get_yt_link()
        response = link
    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    random_video()
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel, starterbot_id)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")