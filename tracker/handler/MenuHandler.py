#!/usr/bin/env python

from utils import shell_colors as shell
from tracker.database import database
from tracker.model import file_repository, peer_repository
import math


class MenuHandler:

	def __init__(self, db_file: str):
		self.db_file = db_file

	def serve(self, choice: str) -> None:
		""" Handle the peer packet

		:param choice: the choice to handle
		:return: None
		"""

		if choice == "LISTFILES":
			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row

			except database.Error as e:
				print(f'Error: {e}')
				print('The server has encountered an error while trying to serve the request.')
				return

			try:
				files = file_repository.find_all(conn)

				shell.print_green('\nLogged peers files:')
				if not files:
					shell.print_red('There are not logged peers files.')

				for count, shared_file in enumerate(files, 1):
					print(f'{count}] {shared_file["file_name"]} ', end='')
					shell.print_yellow(f'{shared_file["file_md5"]}\n')

			except database.Error as e:
				conn.rollback()
				conn.close()
				print(f'Error: {e}')
				print('The server has encountered an error while trying to serve the request.')
				return

		elif choice == "SHOWPARTS":

			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row

			except database.Error as e:
				print(f'Error: {e}')
				print('The server has encountered an error while trying to serve the request.')
				return

			peer_list = peer_repository.find_all(conn)

			if not peer_list:
				shell.print_red('There are no logged peers.')
				conn.close()
				return
			else:
				shell.print_green('\nList of known peers:')
				for count, peer_row in enumerate(peer_list, 1):
					shell.print_blue(f'{count}]' + peer_row['ip'] + peer_row['port'] + '\n')

			while True:
				index = input('\nPlease select a peer(q to cancel): ')

				if index == 'q':
					print('\n')
					return

				try:
					index = int(index) - 1
				except ValueError:
					shell.print_red(f'\nWrong index: number in range 1 - {len(peer_list)} expected.')
					continue

				if 0 <= index <= len(peer_list):

					chosen_peer = peer_list.pop(index)

					peer_session_id = chosen_peer['session_id']

					file_rows = file_repository.get_all_peer_files(conn, peer_session_id)

					if not file_rows:
						shell.print_red('This peer has no file\'s parts')
						conn.close()
						return

					for count, file_row in enumerate(file_rows, 1):
						file_name = file_row['file_name']
						file_md5 = file_row['file_md5']

						part_list = bytearray(file_repository.get_part_list_by_file_and_owner(conn, file_md5, peer_session_id))

						print(f'{count}] ', end='')
						shell.print_blue(f'{file_name}|{file_md5} -> ', end='')

						for byte_index in range(len(part_list)):
							print(f'{bin(part_list[byte_index])[2:]} ', end='')
						print('')
					return()
				else:
					shell.print_red(f'\nWrong index: number in range 1 - {len(peer_list)} expected.')
					continue

		elif choice == "LISTPEERS":
			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row

			except database.Error as e:
				print(f'Error: {e}')
				print('The server has encountered an error while trying to serve the request.')
				return

			try:
				peer_list = peer_repository.find_all(conn)

				if not peer_list:
					shell.print_red('There are not logged peers.')
					conn.close()
					return

				else:
					shell.print_green('\nList of known peers:')
					for count, peer_row in enumerate(peer_list, 1):
						shell.print_blue(f'{count}]' + peer_row['ip'] + peer_row['port'] + '\n')

			except database.Error as e:
				conn.rollback()
				conn.close()
				print(f'Error: {e}')
				print('The server has encountered an error while trying to serve the request.')
				return

		else:
			pass
