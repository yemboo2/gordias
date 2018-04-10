# cb.py
# gordias
# By Markus Ehringer
# Date: 10.03.2018

import requests
import json
import os
import utils
from nameparser import HumanName

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from source_class import Source

class CrunchBase(Source):    

    def get_data(self):
        person_data = self.get_person_data()
        if person_data:
            organization_data = self.get_organization_data(person_data["organization_name"])   
            if not organization_data:
                organization_data = self.get_organization_data(self.organization)
            person_data.update(organization_data)
        return person_data


    def get_person_data(self):
        while True:
            response = requests.request("GET", base_url + odm_people + "name=" + self.first_name + " " + self.last_name +  "&user_key=" + user_key)
            if response.status_code != 401: # Workaround: sometimes '401 - Unauthorized user_key'
                break

        response_json = json.loads(response.text)
        person_list = response_json["data"]["items"]
        #new_persons = list() # less strict variant 
        
        for person in person_list:
            person = person["properties"]
            f_name = HumanName(person["first_name"] + " " + person["last_name"]).first # CB stores titles in the first_name field *sigh*
            if (self.first_name == f_name) & (self.last_name == person["last_name"]):
                if (utils.sim(self.organization, person["organization_name"], 2/3) |
                    utils.sim(self.organization, person["title"], 2/3)): # title = job
                    return person
                #if not person["organization_name"]: # If orga couldn't match because oganization_name = "" add to list
                #    new_persons.append(person)

        #if len(new_persons) == 1:
            #return new_persons[0]

        return dict()


    def get_organization_data(self, crunchbase_organization_name = ""):
        new_organization = dict()

        if not crunchbase_organization_name:
            return new_organization

        response = requests.request("GET", base_url + odm_organization + "name=" + crunchbase_organization_name 
            + "&user_key=" + user_key)
        response_json = json.loads(response.text)
        organization_list = response_json["data"]["items"]

        if len(organization_list) != 0:
            orga = organization_list[0]["properties"]   # First is most relevant
            if (orga["primary_role"] == "company") | (orga["primary_role"] == "school"):
                for key in orga.keys():
                    new_organization["orga_" + key] = orga[key] # Add 'orga_' as key prefix to prevent same key names (with person_data keys)

        return new_organization


def get_crunchbase_config():
    global base_url, odm_people, odm_organization, user_key
    with open(os.path.dirname(__file__) + '/crunchbaseconfig.json', 'r') as crunchbase_config_file:
        crunchbase_config_json = json.load(crunchbase_config_file)

    base_url = crunchbase_config_json["base_url"]
    odm_people = crunchbase_config_json["odm_people"]
    odm_organization = crunchbase_config_json["odm_organization"]
    user_key = crunchbase_config_json["user_key"]

get_crunchbase_config()