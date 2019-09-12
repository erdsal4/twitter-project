import json
from tweepy import Cursor
from twitter_client import get_twitter_client

#   Mine tweets from user timeline

def get_tweets(request_count, username,last_id = None,count = 200, page = 16):
	client = get_twitter_client()
	fname = "user_timeline_{}.json1".format(username+str(request_count))

	with open(fname,"w") as f:
		for page in Cursor(client.user_timeline, screen_name = username, since = last_id, tweet_mode='extended', count = count).pages(page):
			for status in page:
				f.write(json.dumps(status._json)+ "\n")
                
                