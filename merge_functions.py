# merge_functions.py
# gordias
# By Markus Ehringer
# Date: 29.03.2018

from collections import Counter
import notnull

def no_merge(contact_id, current_value, new_source_value_map):
	''' first_name and last_name '''
	return current_value

def collect_emails(contact_id, current_value, new_source_value_map):
	''' email - People can have multiple emails but only one per domain'''
	email_list = list() 
	for source, value in new_source_value_map.items():
		for email in email_list:
			if email.split('@')[1] == value.split('@')[1]:
				continue
			email_list.append(value)

	if not email_list:
		return ""
	return ', '.join(email_list) 

def best_field(contact_id, current_value, new_source_value_map):
	''' city, country '''
	weighted_field_count_dict = dict()
	for source, value in new_source_value_map.items():
		if value in weighted_field_count_dict:
			weighted_field_count_dict[value] += notnull.get_nn_score(contact_id, source)
		weighted_field_count_dict[value] = notnull.get_nn_score(contact_id, source)

	if not weighted_field_count_dict:
		return ""

	return max(weighted_field_count_dict, key = weighted_field_count_dict.get)

def union_keywords(contact_id, current_value, new_source_value_map):
	if current_value:
		keyword_list = current_value.split(', ')
	else:
		keyword_list = list()
	
	for source, value in new_source_value_map.items():
		if value:
			keyword_list = list(set().union(keyword_list, value.split(', ')))
	
	return ', '.join(keyword_list)

def best_twitter_link(contact_id, current_value, new_source_value_map):
	''' twitter_url '''
	return best_link(current_value, new_source_value_map, "twitter")

def best_crunchbase_link(contact_id, current_value, new_source_value_map):
	''' crunchbase_url '''
	return best_link(current_value, new_source_value_map, "crunchbase")

def best_xing_link(contact_id, current_value, new_source_value_map):
	''' xing_url '''
	return best_link(current_value, new_source_value_map, "xing")

def best_linkedin_link(contact_id, current_value, new_source_value_map):
	''' linkedin_url '''
	return best_link(current_value, new_source_value_map, "linkedin")

def best_facebook_link(contact_id, current_value, new_source_value_map):
	''' facebook_url '''
	return best_link(current_value, new_source_value_map, "facebook")

def best_link(current_value, new_source_value_map, website_name):
	''' twitter_url, crunchbase_url, xing_url, linkedin_url, facebook_url '''
	link_list = list()
	for source, value in new_source_value_map.items():
		link_list.append(value)
		if (website_name == source.lower):
			return value

	if not link_list:
		return ""
	
	link_count_dict = Counter(link_list)
	return max(link_count_dict, key = link_count_dict.get)

def collect_images(contact_id, current_value, new_source_value_map):
	''' image_urls - The more pictures the better '''
	if current_value:
		image_url_list = current_value.split(", ")
	else:
		image_url_list = list()

	for source, value in new_source_value_map.items():
		if value in image_url_list:
			continue
		image_url_list.append(value)

	if not image_url_list:
		return ""
	return ', '.join(image_url_list)
