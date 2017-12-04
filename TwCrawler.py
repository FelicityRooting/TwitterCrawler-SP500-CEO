#!/usr/bin/env python
# encoding: utf-8

import csv

# import os
# os.chdir('D:\workspace\TwCrawler')
# sys.path.append("D:/workspace/GitHub/tweepy")
import tweepy  # https://github.com/tweepy/tweepy <- imported from GitHub Clone D:\workspace\GitHub\Tweepy

XXXXXXXXXXXXXXXXXXXXXXXXX
# Twitter API credentials
consumer_key = "XXXXXXXXXXXXXXXXXXXXXXXXX"
consumer_secret = "XXXXXXXXXXXXXXXXXXXXXXXXX"
access_key = "XXXXXXXXXXXXXXXXXXXXXXXXX"
access_secret = "XXXXXXXXXXXXXXXXXXXXXXXXX"

# User name to be fetched
# Elon Musk / @elonmusk
# username = "elonmusk"
# username = "khala06896201"

# Twitter only allows access to a users most recent 3240 tweets with this method
def get_all_tweets(twitter_id):
    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=twitter_id, count=200)

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:  #  <- use this loop when others are fine.
    # while False:
        print("getting tweets before %s" % oldest)

        # all subsequent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name=twitter_id, count=200, max_id=oldest)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        print("...%s tweets downloaded so far" % (len(alltweets)))

    # transform the tweepy tweets into a 2D array that will populate the csv
    outtweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in alltweets]
    print(outtweets)
    return outtweets

def getAllTweetsToCsv(twitter_id):
    out = get_all_tweets(twitter_id)

    # write the csv
    with open('%s_tweets.csv' % twitter_id, 'w') as f:
        writer = csv.writer(f)
        writer.writerow([b'id', b'created_at', b'text'])
        writer.writerows(out)


if __name__ == '__main__':
    # pass in the username of the account you want to download
    get_all_tweets(username)
