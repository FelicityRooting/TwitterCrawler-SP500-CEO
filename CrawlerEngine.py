#!/usr/bin/env python
# encoding: utf-8

# INPUT:    a 'userid.txt' file, with each userid per line.
#           an existing 'alltweets.csv' file, with previously crawled tweets.
# OUTPUT:   updated 'alltweets.csv' file, with the INPUT userid's tweets crawled and saved into.


import os
import time
import pandas
from tweepy import error

# sys.path.append("D:\workspace\TwCrawler")
import TwCrawler

os.chdir(os.path.abspath('D:\computer science'))
fname = os.path.abspath(os.path.join(os.getcwd() + '\\' + 'userid.txt'))
try:
    with open(fname, 'r') as f:
        userid = f.readlines()
        print(len(userid),'UserID\'s Connected.')
except:
    print('FILE NOT FOUND!')


# dataTemplate = {'id' : [], 'tweetId' : [], 'time' : [], 'content' : []}
# alltweets = pandas.DataFrame(data = dataTemplate)

# @useridList: userid's that have been crawled
alltwits = pandas.read_csv('alltweets.csv')
useridList = list(alltwits['id'].drop_duplicates())

# loop through userid's in userid.txt and call crawler method
for currUser in userid:
    id = '@' + currUser.strip()
    if id not in useridList:
        print('Crawling:',id)
        try:
            tweets = TwCrawler.get_all_tweets(id)
        except IndexError:
            print('User has not tweeted yet.')
            continue
        except error.TweepError:
            print('User ID mismatched.')
            continue

        currUserTweets = pandas.DataFrame(tweets)
        currUserTweets = currUserTweets.assign(userid = id)
        currUserTweets.columns = ['tweetId', 'time', 'content', 'id']
        currUserTweets.to_csv('alltweets.csv', header=False, index=False, mode='a')

        time.sleep(1)
    else:
        print(id, 'is already in the database. Skip to next user.')