# twitter oauth test

#用Tweepy抓取twitter数据
import tweepy #https://github.com/tweepy/tweepy
import csv


#Twitter API credentials
consumer_key = "SAHnTZbkW1B3gCR7l4hBPapVR"
consumer_secret = "UMXUFeiYAddSQAFjPP10VX9eDb40QSSlVLAF1f6VFPz2G5oM3j"
access_key = "918549121853779968-r0WlJS4XWhuHL9ReLLhcflFuMZQ7B4f"
access_secret = "6eSW5CM8HSHTeRtAPHCSVziM3WbbjiRoz4vgFh8hFJ3kG"


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)

api = tweepy.API(auth)
api.update_status('tweepy + oauth!')

