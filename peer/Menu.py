#!/usr/bin/env python

from peer.handler import MenuHandler
from utils import shell_colors
from peer.LocalData import LocalData



class Menu:

	def __init__(self, handler: MenuHandler):
		self.handler = handler

	def show(self) -> None:
		""" Shows the menu that interacts with the user

		:return: None
		"""

		choice = ''
		while choice != 'q':
			print('\n- Main Menù -----------------------')
			print('| <1> Search a file to download   |')
			print('| <2> Share a file                |')
			print('-----------------------------------')
			choice = input('Select an option (q to logout): ')

			if choice in {'1', '2'}:
				if choice == '1':
					command = 'LOOK'
				elif choice == '2':
					command = 'ADDR'

				self.handler.serve(command)

			if choice == 'q':

				self.handler.serve('LOGO')
				if LocalData.tracker_is_empty():
					break
				else:
					continue

			elif choice != 'q':
				shell_colors.print_red('Input code is wrong. Choose one action!\n')

		shell_colors.print_blue('\nBye!\n')
