# tw.py
# gordias
# By Markus Ehringer
# Date: 09.03.2018

import twitter
import json
import os
import utils


def setup_twitter_api():
    global api
    with open(os.path.dirname(__file__) + '/twitterconfig.json', 'r') as twitter_config_file:
        twitter_config_json = json.load(twitter_config_file)

    api = twitter.Api(consumer_key = twitter_config_json["consumer_key"], 
                      consumer_secret = twitter_config_json["consumer_secret"],
                      access_token_key = twitter_config_json["access_token_key"], 
                      access_token_secret = twitter_config_json["access_token_secret"],
                      tweet_mode = 'extended')


def get_data(first_name, last_name, company = ""):
    globals()['first_name'] = first_name
    globals()['last_name'] = last_name
    globals()['company'] = company

    user_data, user_id = get_user_data(first_name, last_name, company)
    tweet_list = get_tweet_data(user_id)
    
    tweets = " ".join(tweet_list)
    user_data["tweets"] = tweets

    return user_data


def get_user_data(first_name, last_name, company = ""):
    new_user = dict()
    user_id = ""
    users = api.GetUsersSearch(term = first_name + " " + last_name)
    
    for user in users:
        if user.name == first_name + " " + last_name: # matching of 'right' user only on name | no company/organization user-field
            new_user["name"] = user.name
            new_user["screen_name"] = user.screen_name
            new_user["location"] = user.location
            new_user["description"] = user.description
            new_user["url"] = user.url
            new_user["profile_image_url"] = user.profile_image_url
            break
    
    return new_user, user.id


def get_tweet_data(user_id):
    tweets= api.GetUserTimeline(user_id = user_id)
    tweet_texts = list()

    for tweet in tweets:
        tweet_texts.append(tweet.full_text)

    return tweet_texts


setup_twitter_api()