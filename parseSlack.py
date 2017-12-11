import csv, json, os, urllib

try:
      SLACK_API_TOKEN = os.environ['SLACK_API_TOKEN']
except:
      print "Missing SLACK_API_TOKEN env."
      exit()    

try:
      SLACK_CHANNEL_ID = os.environ['SLACK_CHANNEL_ID']
except:
      print "Missing SLACK_CHANNEL_ID env."
      exit()      

try:
      CSV_FILENAME = os.environ['CSV_FILENAME']
except:
      print "Missing CSV_FILENAME env."
      exit()

try:
      SEARCH_TEXT = os.environ['SEARCH_TEXT'] 
except:
      SEARCH_TEXT = ''
      pass

url = "https://slack.com/api/channels.history?token=" + SLACK_API_TOKEN + "&channel=" + SLACK_CHANNEL_ID + "&count=100&latest=0"
response = urllib.urlopen(url)

channel_parsed = json.loads(response.read())

message_data = channel_parsed['messages']

# open a file for writing

csv_file = open(CSV_FILENAME, 'w')

# create the csv writer object

csvwriter = csv.writer(hubot_data)

count = 0

for msg in message_data:

      if count == 0:

             header = msg.keys()

             csvwriter.writerow(header)

             count += 1

      msgText = str(msg['text'])
      msgUser = str(msg['user'])

      if msgText.find(SEARCH_TEXT) == 0:

              csvwriter.writerow(msg.values())

csv_file.close()