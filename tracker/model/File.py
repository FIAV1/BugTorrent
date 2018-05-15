#!/usr/bin/env python

from tracker.database import database


class File:

	def __init__(self, file_md5, file_name, len_file, len_part):
		self.file_md5 = file_md5
		self.file_name = file_name
		self.len_file = len_file
		self.len_part = len_part

	def insert(self, conn: database.sqlite3.Connection) -> None:
		""" Insert the file into the db
		:param conn - the db connection
		:return None
		"""
		conn.execute(
			'INSERT INTO files VALUES (?,?,?,?)',
			(self.file_md5, self.file_name, self.len_file, self.len_part)
		)

	def update(self, conn: database.sqlite3.Connection) -> None:
		""" Update the file into the db
		:param conn - the db connection
		:return None
		"""
		query = """UPDATE files
		SET file_name=:name
		WHERE file_md5 =:md5"""

		conn.execute(query, {'md5': self.file_md5, 'name': self.file_name})

	def delete(self, conn: database.sqlite3.Connection) -> None:
		""" Remove the file from the db
		:param conn - the db connection
		:return None
		"""

		conn.execute('DELETE FROM files WHERE file_md5=?', (self.file_md5,))
