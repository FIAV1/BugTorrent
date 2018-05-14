#!/usr/bin/env python

from tracker.database import database
from .Peer import Peer


def find(conn: database.sqlite3.Connection, session_id: str) -> 'Peer':
	""" Retrieve the peer with the given session_id
	:param conn - the db connection
	:param session_id - session id for a peer
	:return peer - first matching result for the research
	"""
	c = conn.cursor()
	c.execute('SELECT * FROM peers WHERE session_id = ?', (session_id,))
	row = c.fetchone()

	if row is None:
		return None

	peer = Peer(session_id, row['ip'], row['port'])

	return peer


def find_all(conn: database.sqlite3.Connection) -> list():
	""" Retrieve all the peers
	:param conn - the db connection
	:return list - all the peers
	"""
	c = conn.cursor()
	c.execute('SELECT * FROM peers')
	peer_rows = c.fetchall()

	return peer_rows


def find_by_ip(conn: database.sqlite3.Connection, ip: str) -> 'Peer':
	""" Retrieve the peer with the given session_id
	:param conn - the db connection
	:param session_id - session id for a peer
	:return peer - first matching result for the research
	"""
	c = conn.cursor()
	c.execute('SELECT * FROM peers WHERE ip = ?', (ip,))
	row = c.fetchone()

	if row is None:
		return None

	peer = Peer(row['session_id'], ip, row['port'])

	return peer


def get_peer_by_file(conn: database.sqlite3.Connection, file_md5: str) -> Peer:
	""" Retrieve all the peers that have the given file
	:param conn - the db connection
	:param query - keyword for the search
	:return: peer matching the research term
	"""
	c = conn.cursor()

	c.execute(
		'SELECT p.session_id, p.ip, p.port '
		'FROM peers AS p NATURAL JOIN files AS f_p '
		'WHERE f_p.file_md5 = ?',
		(file_md5,)
	)
	row = c.fetchone()

	if row is None:
		return None

	peer = Peer(row['session_id'], row['ip'], row['port'])

	return peer
