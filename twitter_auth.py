#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 18:40:39 2019

@author: macintosh
"""

from tweepy import API
from tweepy import OAuthHandler

# Authorize to access twitter API

def get_twitter_auth():
	''' Setup twitter authentication 
	return: tweety.OAuthHandler object
	'''

	consumer_key = ""
	consumer_secret = ""
	access_token = ""
	access_token_secret = ""

	auth = OAuthHandler(consumer_key, consumer_secret)
	# Setting your access token and secret
	auth.set_access_token(access_token, access_token_secret)
	return auth

def get_twitter_client():

	"""
	setup twitter API client.
	return: tweepy.API object
	"""
	auth = get_twitter_auth()
	client = API(auth)
	return client