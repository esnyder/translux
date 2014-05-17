#!/usr/bin/env python
#Python 2.7

##Documentation
#twitter - https://dev.twitter.com/docs
#twython - http://twython.readthedocs.org/en/latest/
from twython import Twython, TwythonError
from collections import defaultdict

#to keep API keys out of version control create apikeys.py. 
#it onlyneeds to contain the two definitions below
import apikeys, time, sys, os, serial

#requires Authentication as of Twitter API v1.1
twitter = Twython(apikeys.TWITTER_APP_KEY, apikeys.TWITTER_APP_SECRET)

#define what strings you are searching Twitter for and how many of each result you wish to see.
tags = ['#trtt2014', 'tinkerfest', 'RogueHackLab', 'ScienceWorks', '@Soupala']
results_per_tag = 5

def TweetDict(tags, results_per_tag):
	t = {}
	for tag in tags:
		search_results = GetTweets(tag, results_per_tag)
		for tweet in search_results['statuses']:
			#if tweet['id'] not in t:
			t[tweet['id']] = tweet #"%s \n %s \n~@%s" % (tweet['created_at'], tweet['text'].encode('utf-8'), tweet['user']['screen_name'].encode('utf-8'))
	return t	

def GetTweets(String, Count):
	try:
		search_results = twitter.search(q=String, count=Count)
	except TwythonError as e:
		print e
	return search_results



def TweetCleaner(tweetText):
	h = tweetText.find('http')
	if h != -1 and len(tweetText) > 128:
		tweetText = tweetText[0:h-1] + " " + tweetText[h + 24:len(tweetText)]
	if tweetText[0:2] == "RT":
		tweetText = tweetText[3:]
	return tweetText

def BreakToLines(text, lineLength):
	lines = []
	beg = 0
	end = 0
	while (beg + lineLength < len(text)):
		if beg + lineLength < len(text):
			end = text[beg:lineLength + beg].rfind(' ') + beg
			lines.append(text[beg:end])
			beg = end + 1
		else:
			lines.append(text[beg:len(text)])
			beg = len(text)
	return lines

def flushserialin():
    print "Reading from serial port..."
    time.sleep(1)
    while f.inWaiting():
        sys.stdout.write(f.read())
    print

#initialize Serial Port
try:
	#sdev = "/dev/ttyUSB0"
	sdev = "/dev/ttyACM0"
	baud = 9600
	sdelay = 6
	f = serial.Serial(sdev, baud)
	print "Initializing connection to Translux\r\n"
	time.sleep(sdelay)
	serialConnected = True	
except:
	print "Translux not connected. Program will run in Python window only\r\n"
	serialConnected = False

#Initialize Tweets Dictionary and playcount
tweets = {}
tweets.update(TweetDict(tags, results_per_tag))
	#Good info about built in counters http://stackoverflow.com/questions/1692388/python-list-of-dict-if-exists-increment-a-dict-value-if-not-append-a-new-dic
tweets_d = defaultdict(int)
for tweet in tweets:
	tweets_d[tweet] == 0

print len(tweets), "tweets cached"

print tweets_d.keys()[3]

#display a tweet
for t in tweets:
	print "Playcount: ", tweets_d[t]
	tweet = tweets[t]
	text = tweet['text'].encode('utf-8')
	ts = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')) 
	lines = BreakToLines(TweetCleaner(text), 32)
	for i in range(len(lines[:5])):
		print lines[i]
		if serialConnected:
			f.write("s%d%s\r\n" % (i+1, msg[i]))
			flushserialin()
	time.sleep(1) #amount of seconds to display each message
	print "\n"
	#for line in BreakToLines(text, 32):
	#	print line
	#print "--@ %s --" % (s['user']['screen_name'].encode('utf-8'))


if serialConnected:
	print "Requesting current msg data..."
	f.write("r")
	flushserialin()
	f.close()