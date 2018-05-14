#!/usr/bin/env python


class LocalData:
	""" Data class containing data structures and methods to interact with them """

	# 'session_id'
	session_id = str()

	# ('ipv4', 'ipv6', 'port')
	tracker = tuple()

	# (file_md5, filename)
	shared_files = list()

	# tracker management ------------------------------------------------------------
	@classmethod
	def get_tracker(cls) -> tuple:
		return cls.tracker

	@classmethod
	def set_tracker(cls, tracker: tuple) -> None:
		cls.tracker = tracker

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
		cls.shared_files.append((file_md5, filename))

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
# ---------------------------------------------------------------------------------
