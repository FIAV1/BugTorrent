#!/usr/bin/env python


class LocalData:
	""" Data class containing data structures and methods to interact with them """

	session_id = str()

	# ('ipv4', 'ipv6', 'port')
	tracker = tuple()

	# tracker management ------------------------------------------------------------
	@classmethod
	def set_tracker(cls, ip4: str, ip6: str, port: int) -> None:
		cls.tracker = (ip4, ip6, port)

	@classmethod
	def get_tracker(cls) -> tuple:
		return cls.tracker
	# -----------------------------------------------------------------------------

	# session_id management ------------------------------------------------------------
	@classmethod
	def set_session_id(cls, session_id: str) -> None:
		cls.session_id = session_id

	@classmethod
	def get_session_id(cls) -> str:
		return cls.session_id
	# -----------------------------------------------------------------------------
