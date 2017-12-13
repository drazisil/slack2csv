import argparse
import csv
from datetime import datetime
import json
import os
import requests


def fetch_from_slack(token, channel, last):
    results = []

    r = requests.get("https://slack.com/api/channels.history?token=" +
                     token + "&channel=" + channel + "&count=100&latest=0")

    channel_parsed = r.json()

    message_data = channel_parsed['messages']

    if len(results) == 0:
        results = message_data
    else:
        results.append(message_data)

    return results


def main():

    parser = argparse.ArgumentParser(description='slack2csv')
    parser.add_argument('--text', help='text to search for', default='')
    parser.add_argument('--last', help='unix timestamp to go back', default='')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument(
        '--token', help='Slack API token', required=True)
    requiredNamed.add_argument(
        '--channel', help='Slack channel id', required=True)
    requiredNamed.add_argument(
        '--filename', help='CSV filename', required=True)
    args = parser.parse_args()

    messages = fetch_from_slack(args.token, args.channel, args.last)

    # open a file for writing

    csv_file = open(args.filename, 'w')

    # create the csv writer object

    csvwriter = csv.writer(csv_file)

    count = 0

    for msg in messages:

        msgText = msg.get('text')

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

    print('Last timestamp: ', last_timestamp)

    csv_file.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
