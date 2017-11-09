# twitter oauth test

import tweepy #https://github.com/tweepy/tweepy
import csv

consumer_key = "EoV50LfF854f2DFPr6FGpQq26"
consumer_secret = "J2rDWovgDHy7Xa4IlFJ0M8AGGzN4f8458V4yQnOE0GfVtrcFaV"
access_key = "918550319726059526-9qFOpZBPDCn0xlV7fF0iEYj4uahdTCf"
access_secret = "zsFhlIfkJsysXsLfJzBreerrOl9VFJ1Koyc3QuVnQaCQz"


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)

api = tweepy.API(auth)
api.update_status('tweepy + oauth!')

