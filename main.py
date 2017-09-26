#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, send_from_directory, session, redirect, \
        request, render_template, abort, jsonify, url_for

import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.tokenize import RegexpTokenizer

from geopy.geocoders import GoogleV3

import re

geolocator = GoogleV3()

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY=''
))

TWEEPY_CONSUMER_KEY = ''
TWEEPY_CONSUMER_SECRET = ''
TWEEPY_ACCESS_TOKEN_KEY = ''
TWEEPY_ACCESS_TOKEN_SECRET = ''

auth = tweepy.OAuthHandler(TWEEPY_CONSUMER_KEY, TWEEPY_CONSUMER_SECRET)
auth.set_access_token(TWEEPY_ACCESS_TOKEN_KEY, TWEEPY_ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

toker = RegexpTokenizer(r'((?<=[^\w\s])\w(?=[^\w\s])|(\W))+', gaps=True)


class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status


@app.route('/', methods=['GET'])
def dashboard():
    return render_template('home.html')

@app.route('/json', methods=['GET'])
def get_wordcloud():
    searchword = request.args.get('place', '')
    address, (latitude, longitude) = geolocator.geocode(searchword)

    data = collect_data(latitude, longitude)
    result = process_data(data)

    return jsonify(msg=result)

def collect_data(latitude, longitude):
    geo_str = '%f,%f,1km' % (latitude, longitude)

    data = str()
    public_tweets = api.search(q='', geocode=geo_str, result_type='recent', count=100)
    for tweet in public_tweets:
        data = data + tweet.text

    geo_str = '%f,%f,10km' % (latitude, longitude)
    public_tweets = api.search(q='', geocode=geo_str, result_type='mixed', count=100)
    for tweet in public_tweets:
        data = data + tweet.text

    return data

def collect_streaming_data(latitude, longitude):
    l = StdOutListener()
    stream = Stream(auth, l)
    stream.filter(locations=[latitude - 1.5, longitude - 1.5, latitude + 1.5, longitude + 1.5])

def process_data(original):
    # Remove http link
    result = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', original)

    # remove punctuation
    result = toker.tokenize(result)

    # remove stop word
    result = filter(lambda w: not w in set(stopwords.words('english')), result)

    # filter noun
    result = [word for word, pos in pos_tag(result) if pos == 'NNP']

    # only use thost noun length > 3
    result = [x for x in result if len(x) > 3]

    cnt = dict()
    for w in result:
        if w not in cnt:
            cnt[w] = 0
        cnt[w] = cnt[w] + 1

    return sorted(cnt.items(), key=lambda x: x[1], reverse=True)[0:150]

if __name__ == '__main__':
    app.run(host='0.0.0.0')
