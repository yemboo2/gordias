# map_functions.py
# gordias
# By Markus Ehringer
# Date: 26.03.2018


TWITTER_URL_BASE = "https://twitter.com/"

# Add Twitter base url as prefix
def to_twitter_profil_url(user_name):
	return TWITTER_URL_BASE + user_name