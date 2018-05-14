#!/usr/bin/env python


class LocalData:
	""" Data class containing data structures and methods to interact with them """

	# 'session_id'
	session_id = str()

	# ('ipv4', 'ipv6', 'port')
	tracker = tuple()

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
