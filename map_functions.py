# map_functions.py
# gordias
# By Markus Ehringer
# Date: 06.04.2018

from geotext import GeoText
from nameparser import HumanName
from pycountry_convert import (country_alpha2_to_country_name, country_alpha3_to_country_alpha2)
import nltk


def identity(field):
	return field

# 3 letter country code to country name.
def country_code(country_code):
	if not country_code:
		return ""

	country = country_code	# If it's no 3 letter country code it is just passed
	if len(country_code) == 3:
		print("3")
		country = country_alpha3_to_country_alpha2(country_alpha2_to_country_name(country_code))
	elif len(country_code) == 2: 	# In case it is just a 2 letter code.
		print("2")
		country = country_alpha2_to_country_name(country_code)

	return country

# Splits the name and returns first name
def name_split_first(name):
	return HumanName(name).first

# Split the name and returns last name
def name_split_last(name):
	return HumanName(name).last

# Splits the location and returns the city
def location_split_city(location):
	places = GeoText(location)
	if places.cities:
		return places.cities[0]
	return ""

# Splits the location and returns the country
def location_split_country(location):
	places = GeoText(location)
	if places.countries:
		return places.countries[0]
	return ""

# Extracts keywords of a text
def extract_keywords(text):
	if not text:
		return ""
	no_keywords_list = ["@", "https", "http", "RT"]
	tokens = nltk.word_tokenize(text)
	tagged = nltk.pos_tag(tokens)
	tag_filtered_word_list = list()
	
	for word, tag in tagged:
		if (tag[0] == 'N'):
				tag_filtered_word_list.append(word)
	
	priortized_words = dict()
	for word in tag_filtered_word_list:
		if word in no_keywords_list:
			continue
		elif word in priortized_words:
			priortized_words[word] += 1
		else:
			priortized_words[word] = 1
	
	word_counter_list = list(map(lambda x: x[1], priortized_words.items()))
	treshhold = ((max(word_counter_list) + min(word_counter_list)) // 2)
	keywords_list = list()
	
	for word, word_counter in priortized_words.items():
		if word_counter > treshhold:
			keywords_list.append(word)
	
	return ', '.join(keywords_list)