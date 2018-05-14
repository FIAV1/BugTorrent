#!/usr/bin/env python

from tracker.database import database


class File:

	def __init__(self, session_id, file_md5, file_name, part_list):
		self.file_md5 = file_md5
		self.file_name = file_name
		self.session_id = session_id
		self.part_list = part_list

	def insert(self, conn: database.sqlite3.Connection) -> None:
		""" Insert the file into the db
		:param conn - the db connection
		:param None
		"""
		conn.execute('INSERT INTO files VALUES (?,?,?,?)', (self.file_md5, self.file_name, self.session_id, self.part_list))

	def update(self, conn: database.sqlite3.Connection) -> None:
		""" Update the file into the db
		:param conn - the db connection
		:return None
		"""
		query = """UPDATE files
		SET file_name=:name, part_list=:part_list
		WHERE file_md5 =:md5"""

		conn.execute(query, {'md5': self.file_md5, 'name': self.file_name, 'part_list': self.part_list})

	def delete(self, conn: database.sqlite3.Connection) -> None:
		""" Remove the file from the db
		:param conn - the db connection
		:return None
		"""

		conn.execute('DELETE FROM files WHERE file_md5=?', (self.file_md5,))
