#!/usr/bin/env python

from peer.handler import MenuHandler
from utils import shell_colors


class Menu:

	def __init__(self, handler: MenuHandler):
		self.handler = handler

	def show(self) -> None:
		""" Shows the menu that interacts with the user

		:return: None
		"""

		choice = ''
		while choice != 'q':
			print('\n- Main Menù ------------------------------')
			print('| <1> List files                         |')
			print('| <2> List peer\'s file parts             |')
			print('| <3> List logged peers                  |')
			print('------------------------------------------')
			choice = input('Select an option (q to exit): ')

			if choice in {'1', '2', '3'}:
				if choice == '1':
					command = "LISTFILES"
				elif choice == '2':
					command = "SHOWPARTS"
				elif choice == '3':
					command = "LISTPEERS"

				self.handler.serve(command)
			elif choice != 'q':
				shell_colors.print_red('Input code is wrong. Choose one action!\n')

		shell_colors.print_blue('\nBye!\n')
