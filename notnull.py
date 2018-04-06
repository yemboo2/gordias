# notnull.py
# gordias
# By Markus Ehringer
# Date: 29.03.2018

import json
import db
import pickle
import enricher

NN_MATRIX_FILENAME = "nn_matrix"
NN_SCORE_MATRIX_FILENAME = "nn_score_matrix"

def sum_nn_s(contact_id):
	sum_nn = 0

	for source_name in source_name_list:
		sum_nn += nn_matrix[contact_id][source_name]

	return sum_nn

def sum_nn_c(source_name):
	sum_nn = 0

	for contact_id in enricher.contact_id_list:
		sum_nn += nn_matrix[contact_id][source_name]

	return sum_nn

def avg_s(contact_id):
	return sum_nn_s(contact_id) / len(source_name_list)

def avg_c(source_name):
	return sum_nn_c(source_name) / len(enricher.contact_id_list)

def calc_nn_score(contact_id, source_name):
	return avg_c(source_name) / avg_s(contact_id)

def calc_nn_score_matrix():
	for contact_id in  enricher.contact_id_list:
		for source_name in source_name_list:
			try:
				nn_score_matrix[contact_id][source_name] = calc_nn_score(contact_id, source_name)
			except ZeroDivisionError:
				nn_score_matrix[contact_id][source_name] = 0

###############################################################################################

def update_nn_score_matrix(contact_id):
	''' Call after datacollector is called '''
	changed = False
	for source_name in source_name_list:
		sum_nn = avg_sum_nn_sc(contact_id, source_name)
		if nn_matrix[contact_id][source_name] != sum_nn:
			''' True if something changed in the nn_matrix -> calculate nn_source_matrix again '''
			nn_matrix[contact_id][source_name] = sum_nn
			changed = True
	if changed:
		calc_nn_score_matrix()

def avg_sum_nn_sc(contact_id, source_name):
	''' Values are the number of fields not null for a source and contact divided by the number of fields a source contributes to '''
	sum_nn = 0
	database_contact = db.get_contact_by_contact_id(source_name, contact_id)
	
	if not database_contact:
		return 0.0
	
	contact = enricher.database_contact_to_contact_dict(database_contact)
	
	for field_name in source_field_names[source_name]:
		if contact[field_name]:
			sum_nn += 1

	return sum_nn / len(source_field_names[source_name])

def get_nn_score(contact_id, source_name):
	''' Called from merge functions '''
	if contact_id == -1.0:	# In case when two data fields from the same source need to be merged during the data collection process
		return 1
	return nn_score_matrix[contact_id][source_name]

###############################################################################################

def set_source_names_and_source_field_names():
	''' Extract the field names for each source out of the associated mapping.json file - set of all the target names per file '''
	global source_field_names # Keys are the source_names and values are lists of field names
	global source_name_list

	with open('sources/sourcesconfig.json', 'r') as sources_config_file:
		sources_config_json = json.load(sources_config_file)

	source_list = sources_config_json["sources"]
	source_field_names = dict()
	source_name_list = list()

	for source in source_list:
		source_name_list.append(source["name"])
		source_field_name_set = set()
		with open('sources/' + (source["path"].split("/"))[0] + '/mapping.json', 'r') as mapping_data_file:
			mapping = json.load(mapping_data_file)
		for key, value_target_pair_list in mapping.items():
			for value_target_pair in value_target_pair_list:
				source_field_name_set.add(value_target_pair["target"])
		source_field_names[source["name"]] = list(source_field_name_set)		

def load_matrices():
	global nn_matrix
	global nn_score_matrix
	''' nn_score_matrix '''
	try:
		nn_score_matrix = load_matrix(NN_SCORE_MATRIX_FILENAME)
	except (OSError, IOError, FileNotFoundError):
		nn_score_matrix = create_empty_matrix()
	''' nn_matrix '''
	try:
		nn_matrix = load_matrix(NN_MATRIX_FILENAME)
	except (OSError, IOError, FileNotFoundError):
		nn_matrix = create_empty_matrix()
		''' If there is no nn_matrix file but there are contacts, both matrices need to be updated '''
		for contact_id in enricher.contact_id_list:
			update_nn_score_matrix(contact_id)

def load_matrix(file_name):
	with open('obj/' + file_name + '.pkl', 'rb') as f:
		return pickle.load(f)

def create_empty_matrix():
	matrix = dict()
	empty_source_dict = dict()
	for source_name in source_name_list:
		empty_source_dict[source_name] = 0.0

	for contact_id in enricher.contact_id_list:
		matrix[contact_id] = dict(empty_source_dict)
	return matrix

def add_person_to_matrices(contact_id):
	empty_source_dict = dict()
	for source_name in source_name_list:
		empty_source_dict[source_name] = 0.0
	nn_matrix[contact_id] = dict(empty_source_dict)
	nn_score_matrix[contact_id] = dict(empty_source_dict)


def dump_matrices():
	dump_matrix(nn_matrix, NN_MATRIX_FILENAME)
	dump_matrix(nn_score_matrix, NN_SCORE_MATRIX_FILENAME)
	
def dump_matrix(matrix, file_name):
	with open('obj/'+ file_name + '.pkl', 'wb') as f:
		pickle.dump(matrix, f, pickle.HIGHEST_PROTOCOL)


set_source_names_and_source_field_names()
load_matrices()