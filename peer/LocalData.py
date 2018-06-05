#!/usr/bin/env python

import math
import random


class LocalData:
	""" Data class containing data structures and methods to interact with them """

	# 'session_id'
	session_id = str()

	# ('ipv4', 'ipv6', 'port')
	tracker = tuple()

	# (file_md5, filename)
	shared_files = list()

	# [(owner_ipv4', 'owner_ipv6', 'owner_port'), 'part_list_i']
	part_list_table = list()

	# (part_num)
	downloadable_parts = list()

	# bytearray containing the part list regarding the file under download
	downloading_part_list = bytearray()

	# number of parts owned regarding the file under download
	num_parts_owned = int()

	# tracker management ------------------------------------------------------------
	@classmethod
	def get_tracker(cls) -> tuple:
		return cls.tracker

	@classmethod
	def set_tracker(cls, tracker: tuple) -> None:
		cls.tracker = tracker

	@classmethod
	def clear_tracker(cls) -> None:
		cls.tracker = tuple()

	@classmethod
	def tracker_is_empty(cls) -> bool:
		if not cls.tracker:
			return True
		else:
			return False

	@classmethod
	def get_tracker_ip4(cls) -> str:
		return cls.tracker[0]

	@classmethod
	def get_tracker_ip6(cls) -> str:
		return cls.tracker[1]

	@classmethod
	def get_tracker_port(cls) -> int:
		return cls.tracker[2]
	# ----------------------------------------------------------------------------------
	
	# session_id management ------------------------------------------------------------
	@classmethod
	def set_session_id(cls, session_id: str) -> None:
		cls.session_id = session_id

	@classmethod
	def get_session_id(cls) -> str:
		return cls.session_id
	# ---------------------------------------------------------------------------------

	# shared_file management ------------------------------------------------------------
	@classmethod
	def add_shared_file(cls, file_md5: str, filename: str) -> None:
		cls.shared_files.append((file_md5, filename.lower()))

	@classmethod
	def is_shared_file(cls, file_md5: str, filename: str) -> bool:
		if (file_md5, filename) in cls.shared_files:
			return True
		return False

	@classmethod
	def get_shared_files(cls) -> list:
		return cls.shared_files

	@classmethod
	def get_shared_file_md5(cls, file: tuple) -> str:
		return file[0]

	@classmethod
	def get_shared_file_name(cls, file: tuple) -> str:
		return file[1]

	@classmethod
	def get_shared_file_name_from_md5(cls, file_md5: str) -> str:
		shared_files = cls.get_shared_files()
		for file in shared_files:
			if cls.get_shared_file_md5(file) == file_md5:
				return cls.get_shared_file_name(file)

	@classmethod
	def clear_shared_files(cls) -> None:
		cls.shared_files.clear()
	# ---------------------------------------------------------------------------------

	# downloadables_file management ---------------------------------------------------
	@classmethod
	def get_downloadable_file_md5(cls, file: tuple) -> str:
		return file[0]

	@classmethod
	def get_downloadable_file_name(cls, file: tuple) -> str:
		return file[1]

	@classmethod
	def get_downloadable_file_length(cls, file: tuple) -> int:
		return int(file[2])

	@classmethod
	def get_downloadable_file_part_length(cls, file: tuple) -> int:
		return int(file[3])
	# ---------------------------------------------------------------------------------

	# part list table management ------------------------------------------------------
	@classmethod
	def set_part_list_table(cls, part_list_table: list) -> None:
		cls.part_list_table = part_list_table

	@classmethod
	def get_part_list_table(cls) -> list:
		return cls.part_list_table

	# ---------------------------------------------------------------------------------

	# downloading part list management-------------------------------------------------
	@classmethod
	def create_downloading_part_list(cls, part_list_length) -> None:
		cls.downloading_part_list = bytearray(part_list_length)

	@classmethod
	def get_downloading_part_list(cls) -> bytearray:
		return cls.downloading_part_list

	@classmethod
	def set_downloading_part_list(cls, part_list: bytearray) -> None:
		cls.downloading_part_list = part_list

	@classmethod
	def update_downloading_part_list(cls, new_part_num: int):
		# Getting our part list regarding the interest file
		downloading_part_list = LocalData.get_downloading_part_list()

		# Calc the index of the list that must be updated
		byte_index = int(math.floor(new_part_num / 8))
		# Calc the position of the bit to toggle
		bit_index = new_part_num % 8
		# Update our part list
		downloading_part_list[byte_index] |= pow(2, 7 - bit_index)
		cls.set_downloading_part_list(downloading_part_list)

	@classmethod
	def set_num_parts_owned(cls, num_parts_owned: int) -> None:
		cls.num_parts_owned = num_parts_owned

	@classmethod
	def get_num_parts_owned(cls) -> int:
		return cls.num_parts_owned

	@classmethod
	def __get_owned_parts(cls) -> list:
		# Getting our part list regarding the interest file
		# Every element of the list is: ((owner_ip4, owner_ip6, owner_port), part_list))
		downloading_part_list = cls.get_downloading_part_list()
		downloading_part_list_length = len(downloading_part_list)

		# Create a list containing our owned parts regarding the interest file
		owned_parts = list()

		for byte_index in range(downloading_part_list_length):
			for bit_index in range(8):
				bit_mask = pow(2, 7 - bit_index)
				ris = downloading_part_list[byte_index] & bit_mask
				if ris != 0:
					owned_parts.append(byte_index * 8 + bit_index)

		return owned_parts

	@classmethod
	def update_downloadable_parts(cls) -> list:
		# Getting all the available part lists in the network
		# Every element of the list is: ((owner_ip4, owner_ip6, owner_port), part_list))
		part_list_table = cls.get_part_list_table()

		# Getting our part list regarding the interest file
		downloading_part_list = cls.get_downloading_part_list()
		part_list_length = len(downloading_part_list)

		# Creating a list of couple: (num_part, sum)
		occurrency_list = list()

		for byte_index in range(part_list_length):
			for bit_index in range(8):
				sum = 0
				for part_list_tuple in part_list_table:
					part_list = part_list_tuple[1]
					if part_list[byte_index] & pow(2, 7 - bit_index) != 0:
						sum += 1
				occurrency_list.append(((byte_index * 8) + bit_index, sum))
		# Sorting the list according to the sum portion of every couple
		occurrency_list.sort(key=lambda tup: tup[1])

		# Getting the list of owned parts regarding the interest file
		owned_parts = cls.__get_owned_parts()

		# Create the final list, who will contain only the downloadable parts
		downloadable_parts = list()

		for occurrency_row in occurrency_list:
			if occurrency_row[1] == 0:
				# The the part hasn't owners
				continue
			if occurrency_row[0] in owned_parts:
				# We already have the part
				continue
			downloadable_parts.append(occurrency_row[0])

		cls.downloadable_parts = downloadable_parts

	@classmethod
	def get_downloadable_parts(cls) -> list:
		return cls.downloadable_parts

	@classmethod
	def get_owner_by_part(cls, part_num: int) -> tuple:
		# Getting all the available part lists in the network.
		# Every element of the list is: ((owner_ip4, owner_ip6, owner_port), part_list))
		part_list_table = LocalData.get_part_list_table()

		# Create a list containing the owners of the given part_number
		owners = list()

		byte_index = int(math.floor(part_num / 8))
		bit_mask = pow(2, 7 - (part_num % 8))

		for part_list in part_list_table:
			ris = part_list[1][byte_index] & bit_mask
			if ris != 0:
				owners.append(part_list[0])

		return random.choice(owners)
# ---------------------------------------------------------------------------------
