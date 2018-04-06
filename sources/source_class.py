# source_class.py
# gordias
# By Markus Ehringer
# Date: 02.04.2018

import abc

class Source():
	__metaclass__ = abc.ABCMeta

	def __init__(self, first_name, last_name, organization = ""):
		self.first_name = first_name
		self.last_name = last_name
		self.organization = organization

	@abc.abstractmethod
	def get_data():
		pass