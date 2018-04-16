# gordias

This prototype takes the information of several APIs, transforms it and stores it in a data warehouse. The gathered data then can be requested over an API.

## Getting Started

### Prerequisites

To setup and run the project we first need to get [Docker](https://www.docker.com/community-edition#/download) and [Docker compose](https://docs.docker.com/compose/install/#prerequisites).

### Installing

Executing the docker-compose file will setup the postgres database in one container (incl. creating the necessary tables) and the python environment in another container and execute the application.

Clone the project,

```
git clone https://github.com/yemboo2/gordias.git
```

change to the _gordias_ folder and run docker-compose.

```
cd goridas && sudo docker-compose up
```

Verfiy setup:

```
curl --data "contacts={\"contacts\" : [{\"first_name\" : \"Markus\",\"last_name\" : \"Ehringer\",\"organization\" : \"Technical University of Munich\"}]}" http://localhost:8080/contacts --data "age=1"
```

## Deployment

### API

The API has two endpoints:

* _contact_: Enriches a single contact (POST-request). Parameters are first name, last name and organization.
* _contacts_: Enriches multiple contacts (POST-request). Parameter is a string in JSON format containing a list of basic contact fields: for each contact which should be enriched we need first name, last name and organization.

First name and last name and organization must be provided in every case. Both endpoints return a JSON object with the found contact fields.

An additional parameter _age_ can be added to each request. Providing this information the user can define how old the enriched data can be. If the last synchronization time of a contact lies further back than the time of the request subtracted by the age the data will be synchronized with the sources. The value of this parameter is specified in hours.

_Note1_: Make sure to use HTML encoding for the data sent to the API.
_Note2_: It could take a while after the start until the first request will be processed.

### Adding new sources

1. Create a new folder in the _sources_ directory.
2. Create a new python file in that folder.
3. Create a class which inherits from the class defined in the _source\_class.py_ file and implement the _get\_data()_ function.
4. Add a new entry to the _sources\_config.json_ file.
	1. _name_: Simply the name of the source (only letters).
	2. _path_: Path to the file that contains the class _class\_name_.
	3. _class\_name_: Name of the class that inherits from the abstract source class.
5. Adding a mapping configuration file _mapping.json_.
6. If needed add an additional file _map\_functions.py_ with source-specific map functions.

Importing the abstract class from the folder above is a bit tricky. If you have troubles check out an existing source (e.g. Twitter(_/tw_)).If you plan to overwrite the constructor of the abstract class in the subclass make sure to pass first\_name, last\_name and organization and set these as class variables (see source\_class.py).

The _class\_name_ file has to contain the logic to fetch data from the actual source. When retrieving multiple user from APIs matching the right one based on just the name and organization might be difficult. The _utils.py_ contains some functions to support the matching process. In doubt if you match the correct person there are two options: Taking the contact and risk having maybe wrong data in the system or taking no contact and risk maybe losing correct data. So far we stuck to the latter option. All added sources have to stick to that decision.

## Contributing

After locally adding a new source to the project and testing it extensively one can create a pull request for this source to be added. If it meets all requirements it will be merged.

## Authors

* **Markus Ehringer** - *Initial work* - [yemboo2](https://github.com/yemboo2)

## Acknowledgments

Special thanks to my supervisor **Patrick Holl** for his help and inspiring ideas.
