#!/usr/bin/env python
import json


class LocalData:
	""" Data class containing data structures and methods to interact with them """

	json_file = 'peer/data.json'

	session_id = str()

	# ('ipv4', 'ipv6', 'port')
	tracker = tuple(json.load(open('peer/data.json'))["tracker"])

	# friend management ------------------------------------------------------------
	@classmethod
	def set_tracker(cls, tracker: tuple) -> None:
		data = json.load(open(cls.json_file))
		data["tracker"] = tracker
		json.dump(data, open('peer/data.json', 'w'))
		cls.tracker = tracker
	# -----------------------------------------------------------------------------

	# query management-------------------------------------------------------------
	@classmethod
	def get_shared_files(cls) -> list:
		return json.load(open(cls.json_file))["files"]

	@classmethod
	def get_shared_file_name(cls, file: tuple) -> str:
		return file[1]

	@classmethod
	def get_shared_file_md5(cls, file: tuple) -> str:
		return file[0]

	@classmethod
	def get_shared_file_name_from_md5(cls, file_md5: str) -> str:
		shared_files = cls.get_shared_files()
		for file in shared_files:
			if cls.get_shared_file_md5(file) == file_md5:
				return cls.get_shared_file_name(file)

	@classmethod
	def add_shared_file(cls, file_md5: str, file_name: str) -> None:
		data = json.load(open(cls.json_file))
		data["files"].append((file_md5, file_name))
		json.dump(data, open("peer/data.json", "w"))

	@classmethod
	def is_shared_file(cls, file: tuple) -> bool:
		data = json.load(open(cls.json_file))
		if data["files"].count(list(file)) > 0:
			return True
		return False

	@classmethod
	def get_shared_file(cls, index: int) -> tuple:
		data = json.load(open(cls.json_file))
		return data["files"][index]

	@classmethod
	def remove_shared_file(cls, file: tuple) -> None:
		data = json.load(open(cls.json_file))
		data["files"].remove(list(file))
		json.dump(data, open("peer/data.json", "w"))

	@classmethod
	def clear_backup_data(cls) -> None:
		data = {"files": [], "tracker": []}
		json.dump(data, open("peer/data.json", "w"))
		cls.tracker = tuple()
	# ------------------------------------------------------------------------------
