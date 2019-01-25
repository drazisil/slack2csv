import argparse
import csv
from datetime import datetime, timedelta
import json
import os
from progress.spinner import Spinner
import requests
import time


def lookup_user_id_by_name(token, user_name):
    r = requests.get("https://slack.com/api/users.list?token=" +
                     token)

    user_list_parsed = r.json()["members"]

    for user in user_list_parsed:
        if user["name"] == user_name:
            return user["id"]

    return ""


def lookup_channel_id_by_name(token, channel_name, types=None):
    url = "https://slack.com/api/conversations.list?token=" + token
    if types is not None:
        url += "&types=" + types
    query_url = url

    channel_list_parsed = [None]
    while len(channel_list_parsed) > 0:
        r = requests.get(query_url)
        resp = r.json()

        channel_list_parsed = resp["channels"]

        for channel in channel_list_parsed:
            if channel_name in channel.get("name", channel.get("user", None)):
                return channel["id"]

        next_cursor = resp.get("response_metadata", {}).get("next_cursor", None)
        if next_cursor:
            query_url = url + "&cursor=" + next_cursor
        else:
            break

    return ""


def fetch_from_slack(token, channel, offset):
    results = []
    newest_timestamp = offset
    more_results = True

    spinner = Spinner('Fetching history for ' +
                      channel + ' from ' + str(datetime.fromtimestamp(int(offset))) + ' ')

    while more_results == True:
        print(str(datetime.fromtimestamp(float(newest_timestamp))))
        r = requests.get("https://slack.com/api/conversations.history?token=" +
                         token + "&channel=" + channel + "&count=100&inclusive=true&oldest=" + newest_timestamp)

        channel_parsed = r.json()

        if not channel_parsed['ok']:
            raise ValueError("Error fetching channel history from Slack: ",
                             channel_parsed["error"])

        more_results = channel_parsed["has_more"]

        message_data = channel_parsed['messages']

        # yield interim results
        for message in message_data:
            yield message

        newest_timestamp = message_data[0].get('ts')

        time.sleep(2)
        spinner.next()


def main():

    parser = argparse.ArgumentParser(description='slack2csv')
    parser.add_argument('--text', help='text to search for', default='')
    parser.add_argument(
        '--past_days', help='days to go back', default='1')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument(
        '--token', help='Slack API token', required=True)
    requiredNamed.add_argument(
        '--filename', help='CSV filename', required=True)
    mutuallyExclusiveRequired = parser.add_mutually_exclusive_group(required=True)
    mutuallyExclusiveRequired.add_argument(
        '--channel', help='Slack channel id or name')
    mutuallyExclusiveRequired.add_argument(
        '--user', help='Slack user id or name')
    args = parser.parse_args()

    channel_id = args.channel
    user_id = args.user
    conversation_id = None
    types = "public_channel,private_channel"

    if user_id:
        types = "im"
        if not user_id.startswith("U"):
            id = lookup_user_id_by_name(args.token, args.user)
            if id == "":
                print(user_id, " was not found in the Slack user list. Exiting...")
                return False
            channel_id = id
        else:
            channel_id = user_id

    # Check if this is an id or a name
    if channel_id:
        if not channel_id.startswith("C"):
            id = lookup_channel_id_by_name(args.token, channel_id, types)
            if id == "":
                print(channel_id, " was not found in the Slack channel list. Exiting...")
                return False
            conversation_id = id
        else:
            conversation_id = channel_id

    if conversation_id is None:
        print("Could not find a valid conversation id. Exiting...")
        return False

    time_diff = str((datetime.now() - timedelta(days=int(args.past_days))
                     ).timestamp()).split('.')[0]

    # open a file for writing

    csv_file = open(args.filename, 'w')

    # create the csv writer object

    csvwriter = csv.writer(csv_file)

    count = 0
    last_timestamp = 0

    for msg in fetch_from_slack(args.token, conversation_id, time_diff):

        try:
            msgText = msg.get('text')
        except:
            raise

        if msg.get('subtype') != 'bot_message':
            msgUser = msg.get('user')

            msg.setdefault('subtype', '')

            if msgUser != None and msgText.find(args.text) == 0:

                # Write the header if first row
                if count == 0:

                    header = msg.keys()

                    del msg['subtype']

                    csvwriter.writerow(header)

                    count += 1

                last_timestamp = datetime.fromtimestamp(
                    int(msg.get('ts').split('.')[0]))

                # write the csv row
                csvwriter.writerow(msg.values())

    csv_file.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
