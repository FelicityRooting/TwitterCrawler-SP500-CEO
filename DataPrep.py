#!/usr/bin/env python
# encoding: utf-8

# INPUT:    'alltweets.csv' file
# OUTPUT:   'data.csv'

import re # python通过re模块来实现正则表达式
import os
import time
import pandas as pd
import math

import nltk
from nltk.tokenize import word_tokenize, TweetTokenizer
from nltk.corpus import stopwords
from textblob import TextBlob
# os.chdir('D:\computer science')

# features:
# y1 - y7
# matched y ~ x with DayDiff: 0, 15, 30, 60, 90, 180, 360
# x1            | x2                | x3                | x4                    | x5
# daily tweets  | daily (#)trends   | interactions (@)  | links (http://t.co)   | Day of Year
# x6                    | x7                    | x8    | x9 .. x10
# sentiment: %pos/all   | sentiment: %neg/all   | Year  | reserved for other features
# x11 ... x110 .. x210
# Freq of hot words


# helper method: tokenizeTweets
# @s: string
# @return lst: parse and remove: links, foreign letters, '#' => make
# list of tokens => filter w/ stopwords
def tokenizeTweets(s):
    sentence = s[2:-1] # 把alltweets.csv里content列的b'TWEET' -> TWEET，取出tweet内容
    # 先将正则表达式的字符串形式编译为Pattern实例(删除所有link)
    linkPattern = re.compile('http[s]*://[\w.#&+=/]*')
    # sub:返回sentence的一个拷贝，该串中的所有匹配linkPatten的均被替换成了''
    sentence = linkPattern.sub('', sentence)
    hashtag = re.compile('#')
    # 返回sentence的一个拷贝，该串中所有匹配hashtag的均被替换成''
    sentence = hashtag.sub('', sentence)
    # 替换掉\x01 \xe1之类的
    foreign = re.compile(r'\\x\w\w')
    sentence = foreign.sub('', sentence)

    # import stopwords and merge with customized stopwords and punctuation
    try:
        nltk.download('stopwords') #Download stopwords from the NLTK Book Collection
        # get a set of English stopwords
        # The returned list stopWords contains 153 stopwords
        stop = set(stopwords.words('english'))
    except LookupError:
        print("Stop words importing failure. Select stopwords manually")
        stop = []
    finally:
        # run finally block after custom_stopwords is updated
        custom_stopwords = ['this', 'n', 'r', 'u', '2']
        punctuation = ['!', ',', '', '.', '\\', '?', ':', '\"', '&', '-', '/', '', '(', ')', '\'', '$', '@']
        stop = stop.union(custom_stopwords).union(punctuation)
    # class nltk.tokenize.casual.TweetTokenizer(preserve_case=True, reduce_len=False, strip_handles=False)[source]
    tknz = TweetTokenizer(reduce_len = True, strip_handles = True)  # reduce_len: Replace repeated character
    # sequences of length 3 or greater with sequences of length 3, handles = @XXXX
    tokens = tknz.tokenize(sentence)
    lst = [word.lower() for word in tokens if (word.lower() not in stop)]
    return lst

# helper method: Token Frequencies Updater
# @tokens: a list of string tokens
# @dct: a counter dictionary to be updated word's Freq.
# void function, update the 'tokenFrequencies' table
def updateTokenFrequencies(tokens, dct):
    for token in tokens:
        dct[token] = dct.get(token, 0) + 1


def dataPrep(Xfilename, Yfilename, Ydiff, wordDimension):
    # read input as raw for building X
    raw = pd.read_csv(Xfilename)

    # matching date
    dateMDY = raw.time.str.split(' ', expand=True)[0]
    raw = raw.assign(date=dateMDY)

    # calc. feature for each tweet, then use split-apply-combine (S.A.C.) to calc. daily sum for each feature

    # x1: tweets = posts
    raw = raw.assign(x1=1)

    # x2: trends = #TRENDING
    p = re.compile('#[\w]*')
    matches = raw.content.str.findall(p)
    col = matches.apply(len)
    raw = raw.assign(x2=col)

    # x3: interactions = @OTHER
    p = re.compile('@[\w]*\s')
    matches = raw.content.str.findall(p)
    col = matches.apply(len)
    raw = raw.assign(x3=col)

    # x4: links = "http://t.co"
    p = re.compile('http[s]*://')
    matches = raw.content.str.findall(p)
    col = matches.apply(len)
    raw = raw.assign(x4=col)

    # x5: Day of Year - will parse after S.A.C.
    raw = raw.assign(x5=0)

    # x6 & x7: sentiment positive/negative
    analysisSeries = raw.content.apply(TextBlob)
    sentiment = analysisSeries.apply(lambda x:x.sentiment.polarity)
    subjectivity = analysisSeries.apply(lambda x:x.sentiment.subjectivity) # weighted sentiment
    raw = raw.assign(x6=sentiment)
    raw = raw.assign(x7=(subjectivity * subjectivity))

    # x8: Year - will parse after S.A.C.
    raw = raw.assign(x8=0)

    # x9, x10 - LEAVE BLANK
    raw = raw.assign(x9=0)
    raw = raw.assign(x10=0)

    # progress message
    print('x1-x10 created.')

    # Tokenize all tweets into word~freq. tables:


    tokenFreq = dict()
    for sentence in raw.content:
        updateTokenFrequencies(tokenizeTweets(sentence), tokenFreq)

    sortedTokenFreq = sorted(tokenFreq.items(), key=lambda x:x[1], reverse=True)

    # update x10 - x210
    for iColumn in range(wordDimension):
        if iColumn % 10 == 0:
            print('Processing',iColumn+10,'-th column.')
        token = (sortedTokenFreq[iColumn][0]) # i-th most frequent token
        col = raw.content.apply(lambda x:(1 if token in tokenizeTweets(x) else 0))
        raw.insert(raw.shape[1], iColumn, col)

    # Split-Apply(sum)-Combine
    grouped = raw.groupby('date')
    X = grouped.sum() # 'time', 'content', 'id' attributes were dropped as they cannot sum. 'date' become INDEX of X
    col = pd.to_datetime(X.index, format = '%m/%d/%Y')
    X.insert(0, 'date', col)
    X = X.drop(['tweetId'], axis=1)

    # fix x5 DoY and x8 Year
    X['x5'] = X.date.dt.dayofyear
    X['x8'] = X.date.dt.year

    XColumnNames = ['date']
    for i in range(wordDimension+10):
        XColumnNames.append('x'+str(i))
    X.columns = XColumnNames
    X.index.name = 'row'

    # read Y variables
    Y = pd.read_csv(Yfilename)
    Y['Date'] = pd.to_datetime(Y.Date, format='%m/%d/%Y')

    earliestDate = min(X.date)
    latestDate = max(X.date)

    # subset Y using X's boundaries
    Y = Y[(Y['Date'] >= earliestDate) & (Y['Date'] <= latestDate)]
    Y = Y.reset_index()
    Y.columns = ['index', 'date', 'S&P500(TR)', 'S&P500(NetTR)', 'sp500index']
    Y = Y.drop(['index', 'S&P500(TR)', 'S&P500(NetTR)'], axis=1)

    # interpolating weekend SP500 values
    fullDates = pd.DataFrame(pd.date_range(min(Y.date), max(Y.date)))
    fullDates.columns = ['date']
    Y = pd.merge(fullDates, Y, how='left', on=['date'])

    for i in range(2, Y.shape[0]-2):
        if math.isnan(Y.sp500index[i]):
            Y.sp500index[i] = Y.sp500index[i-2] + Y.sp500index[i+2]

    if Ydiff == 0:
        pass
    else:
        Y = pd.concat([Y.date[:-Ydiff], Y.sp500index[Ydiff:].reset_index()], axis=1, ignore_index=True, join='inner')

    # merge X and Y = data
    data = pd.merge(X, Y, how='left', on=['date'])

    return(data)



if __name__ == '__main__':
    out = dataPrep(Xfilename="alltweets.csv", Yfilename="sp500index.csv", Ydiff=0, wordDimension=100)
out.to_csv('X.csv', 'w')
