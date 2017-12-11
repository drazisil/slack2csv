import argparse, csv, json, os, urllib.request

parser = argparse.ArgumentParser(description='slack2csv')
parser.add_argument('--text', help='text to search for', default='')
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('--token', help='Slack API token', required=True)
requiredNamed.add_argument('--channel', help='Slack channel id', required=True)
requiredNamed.add_argument('--filename', help='CSV filename', required=True)
args = parser.parse_args()

url = "https://slack.com/api/channels.history?token=" + args.token + "&channel=" + args.channel + "&count=100&latest=0"
response = urllib.request.urlopen(url)

channel_parsed = json.loads(response.read())

message_data = channel_parsed['messages']

# open a file for writing

csv_file = open(args.filename, 'w')

# create the csv writer object

csvwriter = csv.writer(csv_file)

count = 0

for msg in message_data:

      if count == 0:

             header = msg.keys()

             csvwriter.writerow(header)

             count += 1

      msgText = str(msg['text'])
      msgUser = str(msg['user'])

      if msgText.find(args.text) == 0:

              csvwriter.writerow(msg.values())

csv_file.close()