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

	file = File(file_md5, row['file_name'], row['len_file'], row['len_part'])

	return file


def find_all(conn: database.sqlite3.Connection) -> list:
	""" Retrieve all the files
	:param conn - the db connection
	:return list - all the files
	"""
	c = conn.cursor()
	c.execute('SELECT * FROM files')
	files_rows = c.fetchall()

	return files_rows


def get_peer_owned_files(conn: database.sqlite3.Connection, session_id: str) -> list:
	""" Get all the files owned by the given peer
	:param conn - the db connection
	:param session_id - the session_id of the peer
	:param source - 1 if we are interest only to files added originally by the peer, 0 if we are interest only to files downloaded by the peer
	:return list - the list of files
	"""
	c = conn.cursor()
	c.execute(
		'SELECT f.* '
		'FROM files AS f NATURAL JOIN files_peers AS f_p '
		'WHERE f_p.session_id=? AND f_p.source=1',
		(session_id,)
	)
	files_rows = c.fetchall()

	return files_rows


def get_all_peer_files(conn: database.sqlite3.Connection, session_id: str) -> list:
	""" Get all the files owned by the given peer
	:param conn - the db connection
	:param session_id - the session_id of the peer
	:param source - 1 if we are interest only to files added originally by the peer, 0 if we are interest only to files downloaded by the peer
	:return list - the list of files
	"""
	c = conn.cursor()
	c.execute(
		'SELECT f.* '
		'FROM files AS f NATURAL JOIN files_peers AS f_p '
		'WHERE f_p.session_id=?',
		(session_id,)
	)
	files_rows = c.fetchall()

	return files_rows


def add_owner(conn: database.sqlite3.Connection, file_md5: str, session_id: str, part_list: bytearray, source: int):
	""" Add the peer with the given session_id as file owner into the pivot table
	:param conn - the db connection
	:param file_md5 - the md5 of the file
	:param session_id - the session id of the owner
	:param part_list - the part list containing the parts owned by the peer
	:param source - 0 or 1 if the peer is the one who shared the file for the first time
	"""
	conn.execute('INSERT INTO files_peers VALUES (?,?,?,?)', (file_md5, session_id, part_list, source))


def delete_peer_files(conn: database.sqlite3.Connection, session_id: str) -> int:
	""" Remove all the files owned by the given peer from the directory and return the amount of files deleted
	:param conn - the db connection
	:param session_id - the session_id of the peer
	:return int - the amount of deleted files
	"""
	c = conn.cursor()
	c.execute('PRAGMA foreign_keys=ON')
	deleted = c.execute(
		'DELETE FROM files '
		'WHERE file_md5 IN '
		'	(SELECT f.file_md5 '
		'	FROM files AS f NATURAL JOIN files_peers AS f_p '
		'	WHERE f_p.session_id=? AND f.file_md5 IN '
		'		(SELECT file_md5 '
		'		FROM files_peers '
		'		GROUP BY(file_md5) '
		'		HAVING COUNT(file_md5) = 1)) ',
		(session_id,)
	).rowcount
	deleted += c.execute('DELETE FROM files_peers WHERE session_id=?', (session_id,)).rowcount

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


def get_all_part_lists_by_file_excluding_owner(conn: database.sqlite3.Connection, file_md5: str, session_id: str) -> list:
	""" Get all the indicated file's part list present in the network, excluding the owner's part list
	:param conn - the db connection
	:param file_md5 - the md5 of the file
	:param session_id - the session id of the owner
	:return list - the list of part_list
	"""
	c = conn.cursor()
	c.execute('SELECT part_list FROM files_peers WHERE file_md5=? AND session_id<>?', (file_md5, session_id))

	part_list_rows = c.fetchall()

	return part_list_rows


def get_part_list_by_file_and_owner(conn: database.sqlite3.Connection, file_md5: str, session_id: str) -> tuple:
	""" Get all the indicated file's part list present in the network, excluding the owner's part list
	:param conn - the db connection
	:param file_md5 - the md5 of the file
	:param session_id - the session id of the owner
	:return list - the list of part_list
	"""
	c = conn.cursor()
	c.execute('SELECT part_list FROM files_peers WHERE file_md5=? AND session_id=?', (file_md5, session_id))

	row = c.fetchone()

	if row is not None:
		return row['part_list']
	else:
		return tuple()


def update_part_list_by_file_and_owner(conn: database.sqlite3.Connection, file_md5: str, session_id: str, part_list: bytearray):
	""" Get all the indicated file's part list present in the network, excluding the owner's part list
	:param conn - the db connection
	:param file_md5 - the md5 of the file
	:param session_id - the session id of the owner
	:param part_list - the updated part_list of the file
	"""

	conn.execute('UPDATE files_peers SET part_list=? WHERE file_md5=? AND session_id=?', (part_list, file_md5, session_id))


def get_peer_part_lists(conn: database.sqlite3.Connection, session_id: str):
	""" Get all the file's part list owned by the peer
	:param conn - the db connection
	:param session_id - the session id of the owner
	:return list - the list of part_list
	"""
	c = conn.cursor()
	c.execute('SELECT part_list FROM files_peers WHERE session_id=?', (session_id,))

	part_list_rows = c.fetchall()

	return part_list_rows


def get_file_owners_count_by_filemd5(conn: database.sqlite3.Connection, file_md5: str) -> int:
	""" Retrieve the number of peers that own some parts of the indicated file
	:param conn - the db connection
	:param file_md5 - the md5 of the file
	:return int - the file amount
	"""

	c = conn.cursor()

	c.execute('SELECT COUNT(file_md5) AS num FROM files_peers WHERE file_md5=?', (file_md5,))

	row = c.fetchone()

	if row is None:
		return 0

	return int(row['num'])


def get_all_part_lists_with_owner_by_filemd5(conn: database.sqlite3.Connection, file_md5: str) -> list:
	""" Retrieve all the part lists with the respective owner of the indicated file
	:param conn - the db connection
	:param file_md5 - the md5 of the file
	:return list - the list of owner + part_list
	"""

	c = conn.cursor()

	c.execute(
		'SELECT p.ip, p.port, f_p.part_list '
		'FROM peers AS p NATURAL JOIN files_peers AS f_p '
		'WHERE f_p.file_md5=?', (file_md5,)
	)

	rows = c.fetchall()

	return rows


def get_part_list_by_filemd5(conn: database.sqlite3.Connection, file_md5: str) -> list:
	""" Get all the indicated file's part list present in the network, excluding the owner's part list
	:param conn - the db connection
	:param file_md5 - the md5 of the file
	:return list - the result row
	"""
	c = conn.cursor()
	c.execute('SELECT part_list FROM files_peers WHERE file_md5=?', (file_md5,))

	row = c.fetchone()

	return row['part_list']
