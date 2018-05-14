#!/usr/bin/env python

from tracker.database import database
from .File import File


def find(conn: database.sqlite3.Connection, file_md5: str) -> 'File':
	""" Retrieve the file with the given md5 from database

	:param: conn - the db connection
	:param: file_md5 - the md5 of the file
	:return: file - the istance of the founded file
	"""
	c = conn.cursor()
	c.execute('SELECT * FROM files WHERE file_md5 = ?', (file_md5,))
	row = c.fetchone()

	if row is None:
		return None

	file = File(file_md5, row['file_name'], row['session_id'], row['part_list'])

	return file


def find_all(conn: database.sqlite3.Connection) -> list():
	""" Retrieve all the files

	Parameters:
		conn - the db connection
	Returns:
		list - all the files
	"""
	c = conn.cursor()
	c.execute('SELECT * FROM files')
	files_rows = c.fetchall()

	return files_rows


def peer_has_file(conn: database.sqlite3.Connection, session_id: str, file_md5: str) -> bool:
	""" Check if the peer with the given session_id actually own the file with the given md5

	:param: conn - the db connection
	:param:	session_id - the session_id of the peer
	:param:	file_md5 - the md5 of the file
	:return: bool - True/False either the peer own the file or not
	"""
	c = conn.cursor()
	c.execute('SELECT * FROM files WHERE file_md5= ? AND session_id= ?', (file_md5, session_id))
	row = c.fetchone()

	if row is None:
		return False

	return True


def delete_peer_files(conn: database.sqlite3.Connection, session_id: str) -> int:
	""" Remove all the files owned by the given peer from the directory and return the amount of files deleted
	:param conn - the db connection
	:param session_id - the session_id of the peer
	:return int - the amount of deleted files
	"""
	c = conn.cursor()
	c.execute('PRAGMA foreign_keys=ON')
	deleted = c.execute('DELETE FROM files WHERE session_id = ?', (session_id,)).rowcount

	return deleted


def get_files_count_by_querystring(conn: database.sqlite3.Connection, query: str) -> int:
	""" Retrieve the number of files whose name match with the query string
	:param conn - the db connection
	:param query - the keyword for the search
	:return int - the file amount
	"""

	c = conn.cursor()

	if query == '*':
		c.execute('SELECT COUNT(file_md5) AS num FROM files')
	else:
		c.execute('SELECT COUNT(file_md5) AS num FROM files WHERE file_name LIKE ?', (query,))

	row = c.fetchone()

	if row is None:
		return 0

	return int(row['num'])


def get_files_by_querystring(conn: database.sqlite3.Connection, query: str) -> list:
	""" Retrieve the files whose name match with the query string, with their copies amount
	:param conn - the db connection
	:param query - keyword for the search
	:return file list - the list of corresponding files
	"""
	c = conn.cursor()

	if query == '*':
		c.execute(
			'SELECT * '
			'FROM files AS f',
		)
	else:
		c.execute(
			'SELECT * '
			'FROM files AS f '
			'WHERE f.file_name LIKE ? ',
			(query,)
		)

	file_rows = c.fetchall()

	return file_rows
