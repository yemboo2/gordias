# datacollector.py
# gordias
# By Markus Ehringer
# Date: 26.03.2018

import importlib
import json
import map_functions
import merge_functions

def collect_data(first_name, last_name, organization):
	with open('sources/sourcesconfig.json', 'r') as sources_config_file:
		sources_config_json = json.load(sources_config_file)

	source_list = sources_config_json["sources"]
	data_map = dict()

	for source in source_list:
		mod = importlib.import_module("sources." + source["folder"] + "." + source["file"])
		data = mod.get_data(first_name, last_name, organization)
		data_map[source["name"]] = map_data(data, source["folder"])
		
	return data_map

def map_data(data, source_folder_name):
	with open('sources/' + source_folder_name + '/mapping.json', 'r') as mapping_data_file:
		mapping = json.load(mapping_data_file)

	with open('field_merge_mapping.json', 'r') as field_merge_mapping_file:
		field_merge_mapping = json.load(field_merge_mapping_file)

	map_function_names = mapping.keys()
	mapped_data = dict()

	for map_function_name in map_function_names:
		try:
			map_function = getattr(map_functions, map_function_name) # TODO: First search the specific map-function-file, then the general map-function-file
		except Exception:
			source_map_functions = importlib.import_module("sources." + source_folder_name + ".map_functions")
			map_function = getattr(source_map_functions, map_function_name)
		for source_target_pair in mapping[map_function_name]:
			try:
				mapped_data_value = map_function(data[source_target_pair["source"]])

				if source_target_pair["target"] in mapped_data:	# Value mapped on the same target field name needs to merged with the appropriate merge function
					merge_function = getattr(merge_functions, field_merge_mapping[source_target_pair["target"]])
					merge_dict = dict()
					merge_dict[source_folder_name] = mapped_data[source_target_pair["target"]]
					merge_dict[source_folder_name + str(2)] = mapped_data_value
					mapped_data[source_target_pair["target"]] = merge_function(None, merge_dict)
				else:
					mapped_data[source_target_pair["target"]] = mapped_data_value
			except KeyError:
				pass
	
	return mapped_data