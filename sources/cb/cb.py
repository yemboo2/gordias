# cb.py
# gordias
# By Markus Ehringer
# Date: 10.03.2018

import requests
import json
import os
import utils


def get_crunchbase_config():
    global base_url, odm_people, odm_organization, user_key
    with open(os.path.dirname(__file__) + '/crunchbaseconfig.json', 'r') as crunchbase_config_file:
        crunchbase_config_json = json.load(crunchbase_config_file)

    base_url = crunchbase_config_json["base_url"]
    odm_people = crunchbase_config_json["odm_people"]
    odm_organization = crunchbase_config_json["odm_organization"]
    user_key = crunchbase_config_json["user_key"]


def get_data(first_name, last_name, company = ""):
    globals()['first_name'] = first_name
    globals()['last_name'] = last_name
    globals()['company'] = company

    person_data = get_person_data()
    if person_data:
        organization_data = get_organization_data(person_data["organization_name"])   
        if not organization_data:
            organization_data = get_organization_data(company)
        person_data.update(organization_data)
    return person_data


def get_person_data():
    response = requests.request("GET", base_url + odm_people + "name=" + first_name + " " + last_name +  "&user_key=" + user_key)
    response_json = json.loads(response.text)
    person_list = response_json["data"]["items"]
    new_persons = list()

    for person in person_list:
        person = person["properties"]
        if (first_name == person["first_name"]) & (last_name == person["last_name"]):
            if utils.similar(company, person["organization_name"], 2/3):
                return person
            new_persons.append(person)

    if len(new_persons) == 1:
        return new_persons[0]

    return dict()


def get_organization_data(crunchbase_organization_name = ""):
    new_organization = dict()

    if not crunchbase_organization_name:
        return new_organization

    response = requests.request("GET", base_url + odm_organization + "name=" + crunchbase_organization_name 
        + "&user_key=" + user_key)
    response_json = json.loads(response.text)
    organization_list = response_json["data"]["items"]

    if len(organization_list) != 0:
        organization = organization_list[0]["properties"]   # First is most relevant
        if (organization["primary_role"] == "company") | (organization["primary_role"] == "school"):
            for key in organization.keys():
                new_organization["orga_" + key] = organization[key] # Add 'orga_' as key prefix to prevent same key names (with person_data keys)

    return new_organization


get_crunchbase_config()