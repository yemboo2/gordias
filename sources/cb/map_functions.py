# map_functions.py
# gordias
# By Markus Ehringer
# Date: 26.03.2018


CRUNCHBASE_URL_BASE = "https://www.crunchbase.com/"

# Add Crunchbase person url as prefix
def to_cb_person_url(web_path):
	return CRUNCHBASE_URL_BASE + web_path

# Add Crunchbase organization url as prefix
def to_cb_organization_url(orga_web_path):
	return CRUNCHBASE_URL_BASE + orga_web_path