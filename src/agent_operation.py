from __future__ import print_function
import argparse
import sys, warnings
import deepsecurity
from deepsecurity.rest import ApiException
from pprint import pprint
# import os
# import time
import requests
import json



class CompGroup:
	def __init__(self, c1ws_host, c1ws_key, api_version):
		# Setup
		if not sys.warnoptions:
			warnings.simplefilter("ignore")
		self.configuration = deepsecurity.Configuration()
		self.configuration.host = c1ws_host
		# Authentication
		self.configuration.api_key['api-secret-key'] = c1ws_key
		self.api_version = api_version
		self.id_list = []

	def get_comp_grp(self, grp_name):
		print("# Extarcting id of computer group: {}".format(grp_name))
		# Initialization
		# Set Any Required Values
		api_instance = deepsecurity.ComputerGroupsApi(deepsecurity.ApiClient(self.configuration))

		try:
			api_response = api_instance.list_computer_groups(self.api_version)
			res = api_response.to_dict()
			for comp_grp in res["computer_groups"]:
				print("Computer Group: {}".format(comp_grp["name"]))
				if comp_grp["name"] == grp_name:
					print("Computer group {} id: {}".format(comp_grp["name"], comp_grp["id"]))
					return comp_grp["id"]
		except ApiException as e:
			print("An exception occurred when calling ComputerGroupsApi.list_computer_groups: %s\n" % e)

	def create_comp_grp(self, grp_name):
		# Initialization
		# Set Any Required Values
		api_instance = deepsecurity.ComputerGroupsApi(deepsecurity.ApiClient(self.configuration))
		computer_group = deepsecurity.ComputerGroup(name=grp_name)
		try:
			api_response = api_instance.create_computer_group(computer_group, self.api_version)
			res = api_response.to_dict()
			pprint(api_response)
			return str(res["id"])
		except ApiException as e:
			print("An exception occurred when calling ComputerGroupsApi.create_computer_group: %s\n" % e)

	def delete_comp_grp(self, grp_name):
		comp_grp_id = comp.get_comp_grp(grp_name)
		self.delete_comp(comp_grp_id)
		# api_instance = deepsecurity.ComputerGroupsApi(deepsecurity.ApiClient(self.configuration))
		# try:
		# 	api_instance.delete_computer_group(comp_grp_id, self.api_version)
		# except ApiException as e:
		# 	print("An exception occurred when calling ComputerGroupsApi.delete_computer_group: %s\n" % e)

	def get_list_comp(self, grp_id):
		self.id_list = []
		api_instance = deepsecurity.ComputersApi(deepsecurity.ApiClient(self.configuration, None))
		try:
			api_response = api_instance.list_computers(self.api_version)

			for comp in api_response.computers:
				if grp_id == comp.group_id:
					print("Computer IDS: {}".format(comp.id))
					self.id_list.append(comp.id)
			print("Computer IDS self.ID_LIST: {}".format(self.id_list))
		except ApiException as e:
			print("An exception occurred when calling ComputersApi.list_computers: %s\n" % e)

	def check_hostname(self, hostname):
		api_instance = deepsecurity.ComputersApi(deepsecurity.ApiClient(self.configuration, None))
		try:
			api_response = api_instance.list_computers(self.api_version)
			for comp in api_response.computers:
				if comp.host_name == hostname:
					print("host {}({}) from staging C1WS".format(comp.host_name, comp.id))
					return True
			else:
				return False
		except ApiException as e:
			print("An exception occurred when calling ComputersApi.list_computers: %s\n" % e)

	def get_comp_id(self, comp_grp_id):
		api_instance = deepsecurity.ComputersApi(deepsecurity.ApiClient(self.configuration, None))
		try:
			api_response = api_instance.list_computers(self.api_version)
			for comp in api_response.computers:
				if comp.group_id == comp_grp_id:
					print("Removing host {}({}) from staging C1WS".format(comp.host_name, comp.id))
					self.id_list.append(comp.id)
			print("Computer IDS self.ID_LIST: {}".format(self.id_list))
		except ApiException as e:
			print("An exception occurred when calling ComputersApi.list_computers: %s\n" % e)

	def delete_comp(self, comp_grp_id):
		'''Delete the Computers from C1WS when no longer needed
		'''
		# self.get_list_comp(grp_id)
		self.get_comp_id(comp_grp_id)
		# creating the api instance
		api_instance = deepsecurity.ComputersApi(deepsecurity.ApiClient(self.configuration))

		pprint('Deleting Computers from C1WS')
		try:
			for id in self.id_list:
				print("Removing computer id: {}".format(id))
				api_response = api_instance.delete_computer(id, self.api_version)
				pprint(api_response)
		except ApiException as e:
			print("An exception occurred when calling ScheduledTasksApi.create_scheduled_task: %s\n" % e)

	def get_agent_file(self, nexus_url, nexus_cred):
		res = requests.get(nexus_url, auth=nexus_cred)
		if res.status_code == 200:
			response = res.json()
		else:
			raise Exception("Failed to get the {} file".format(nexus_url))
		return response




if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Please give argument for Reco scan')
	parser.add_argument("--c1ws_host", type=str, help="C1WS Host name")
	parser.add_argument("--c1ws_key", type=str, help="Api Secret Key")
	parser.add_argument("--version", type=str, help="Api Version")
	# parser.add_argument("--new_comp_grp", type=str, help="New computer group name")
	parser.add_argument("--del_comp_grp", type=str, help="Computer Group name")
	parser.add_argument("--nexus_url", action="store", help="IP address of DSM")
	parser.add_argument("--nexus_cred", nargs="+", help="User Credentials")
	args = parser.parse_args()

	comp = CompGroup(args.c1ws_host, args.c1ws_key, args.version)

	# Create new computer group
	# if args.new_comp_grp != 'false':
	# 	comp_grp_id = comp.create_comp_grp(args.new_comp_grp)
	# 	if os.path.exists(args.file_name):
	# 		os.remove(args.file_name)
	# 	with open(args.file_name, "w") as fin:
	# 		fin.write(comp_grp_id)
	# 	print("Sleeping the code for 2 min")
	# 	time.sleep(120)

	nexus_usr, nexus_pwd = args.nexus_cred
	# delete computer group
	if args.del_comp_grp != 'false':
		comp.delete_comp_grp(args.del_comp_grp)

		# print("Removing Agent File")
		# res = requests.delete(args.nexus_url, auth=(nexus_usr, nexus_pwd))
		# if res.status_code == 204:
		# 	print("{} file has been removed".format(args.nexus_url))
		# 	print("Adding Empty Agent File")
		# 	res = requests.put(args.nexus_url, data=json.dumps([]), auth=(nexus_usr, nexus_pwd))
		# 	if res.status_code == 201:
		# 		print("Added {} Agent file".format(args.nexus_url))
