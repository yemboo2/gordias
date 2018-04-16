# tw.py
# gordias
# By Markus Ehringer
# Date: 26.03.2018

import twitter
import json
import os
import utils
from nameparser import HumanName

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from source_class import Source

class Twitter(Source):    

    def get_data(self):
        user_data= self.get_user_data()
        tweet_list = self.get_tweet_data()
        
        tweets = " ".join(tweet_list)
        user_data["tweets"] = tweets

        return user_data

    def get_user_data(self):
        new_user = dict()
        user_id = ""
        users = api.GetUsersSearch(term = self.first_name + " " + self.last_name)
        users = list(filter(lambda x: ((HumanName(x.name).first == self.first_name) &  (HumanName(x.name).last == self.last_name)), users))
        
        for user in users:
            if (utils.description_orga_sim(user.description, self.organization, 0.5) |
                utils.keyword_in_description(user.description)):
                new_user["name"] = user.name
                new_user["screen_name"] = user.screen_name
                new_user["location"] = user.location
                new_user["description"] = user.description
                new_user["url"] = user.url
                new_user["profile_image_url"] = user.profile_image_url
                self.user_id = user.id
                break
        
        return new_user

    def get_tweet_data(self):
        tweet_texts = list()
        try:
            tweets = api.GetUserTimeline(user_id = self.user_id)
            for tweet in tweets:
                tweet_texts.append(tweet.full_text)
        except twitter.error.TwitterError:
            pass
        finally:
            return tweet_texts    


def setup_twitter_api():
    global api
    with open(os.path.dirname(__file__) + '/twitterconfig.json', 'r') as twitter_config_file:
        twitter_config_json = json.load(twitter_config_file)

    api = twitter.Api(consumer_key = twitter_config_json["consumer_key"], 
                      consumer_secret = twitter_config_json["consumer_secret"],
                      access_token_key = twitter_config_json["access_token_key"], 
                      access_token_secret = twitter_config_json["access_token_secret"],
                      tweet_mode = 'extended')

setup_twitter_api()