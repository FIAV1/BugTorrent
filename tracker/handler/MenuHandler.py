#!/usr/bin/env python

from utils import net_utils, hasher, shell_colors as shell
from tracker.database import database
from tracker.model import file_repository, peer_repository


class MenuHandler:

	def __init__(self, db_file: str):
		self.db_file = db_file

	def serve(self, choice: str) -> None:
		""" Handle the peer packet

		:param choice: the choice to handle
		:return: None
		"""

		if choice == "LISTFILES":
			pass

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
				shell.print_red('There are not logged peers.')
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

					part_list = file_repository.get_peer_part_lists(conn, chosen_peer['session_id'])

					if not part_list:
						shell.print_red('This peer has no file\'s parts')
						conn.close()
						return
					else:
						shell.print_green('\nList of parts:')
						for count, part_list_row in enumerate(part_list, 1):
							shell.print_blue(f'{count}]' +  '\n')

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
