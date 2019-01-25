import argparse
import csv
from datetime import datetime, timedelta
import json
import os
from progress.spinner import Spinner
import requests
import time


QUERY_API_TIMEOUT = 2


def paged_query(url):
    query_url = url
    next_cursor = True
    while next_cursor:
        r = requests.get(query_url)
        resp = r.json()

        yield resp

        next_cursor = resp.get("response_metadata", {}).get("next_cursor", None)
        if next_cursor:
            query_url = url + "&cursor=" + next_cursor
        else:
            break
        time.sleep(QUERY_API_TIMEOUT)


def lookup_user_id_by_name(token, user_name):
    url = "https://slack.com/api/users.list?token=" + token
    for user_resp in paged_query(url):

        user_list_parsed = user_resp["members"]

        for user in user_list_parsed:
            if user["name"] == user_name:
                return user["id"]

    return ""


def lookup_channel_id_by_name(token, channel_name, types=None):
    url = "https://slack.com/api/conversations.list?token=" + token
    if types is not None:
        url += "&types=" + types
    for channel_resp in paged_query(url):

        channel_list_parsed = channel_resp["channels"]

        for channel in channel_list_parsed:
            if channel_name == channel.get("name", channel.get("user", None)):
                return channel["id"]

    return ""


def fetch_from_slack(token, channel, oldest):
    n_messages = 0
    newest = None
    oldest = float(oldest)
    oldest_ts = str(datetime.fromtimestamp(oldest))
    spinner = Spinner('Fetching history for ' +
                      channel + ' from ' + oldest_ts + ' ')

    url = ("https://slack.com/api/conversations.history?token=" + token +
           "&channel=" + channel +
           "&count=100&inclusive=true&oldest=" + str(round(oldest)))
    # records are paged oldest to newest, however the message order
    # within a single response is newest to oldest
    for message_resp in paged_query(url):
        if not message_resp['ok']:
            raise ValueError("Error fetching channel history from Slack: ",
                             message_resp["error"])
        messages = message_resp['messages']
        newest = messages[0].get('ts', time.time())
        n_messages += len(messages)

        for message in reversed(messages):
            yield message
        spinner.next()
    print("\nFetched {0} total messages from {1} to {2}".format(
                n_messages,
                oldest_ts,
                str(datetime.fromtimestamp(float(newest)))))


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

    time_diff = time.mktime((datetime.now() -
                             timedelta(days=int(args.past_days))).timetuple())

    # open a file for writing

    csv_file = open(args.filename, 'w')

    # create the csv writer object

    csvwriter = csv.writer(csv_file)

    count = 0
    last_timestamp = 0
    header = []

    for msg in fetch_from_slack(args.token, conversation_id, time_diff):

        try:
            msgText = msg.get('text')
        except:
            raise

        if msg.get('subtype') != 'bot_message':
            msgUser = msg.get('user')

            if 'subtype' in msg:
                del msg['subtype']

            if msgUser != None and msgText.find(args.text) == 0:

                # Write the header if first row
                if count == 0:
                    header = sorted(msg.keys())

                    csvwriter.writerow(header)

                    count += 1

                last_timestamp = datetime.fromtimestamp(
                    float(msg.get('ts')))

                # write the csv row
                row = [msg.get(k) for k in header]
                csvwriter.writerow(row)

    csv_file.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
