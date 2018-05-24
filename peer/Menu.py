#!/usr/bin/env python

from peer.handler import MenuHandler
from utils import shell_colors
from peer.LocalData import LocalData
from common.ServerThread import ServerThread
from threading import Timer
from peer.utils.SpinnerThread import SpinnerThread


class Menu:

	def __init__(self, handler: MenuHandler, server: ServerThread):
		self.handler = handler
		self.server = server

	def show(self) -> None:
		""" Shows the menu that interacts with the user

		:return: None
		"""

		choice = ''
		while choice != 'q':
			print('\n- Main Menù -----------------------')
			print('| <1> Search a file to download   |')
			print('| <2> Share a file                |')
			print('| <3> Files in sharing            |')
			print('| <4> Your tracker                |')
			print('-----------------------------------')
			choice = input('Select an option (q to logout): ')

			if choice in {'1', '2', '3', '4'}:
				if choice == '1':
					command = 'LOOK'
				elif choice == '2':
					command = 'ADDR'
				elif choice == '3':
					command = 'SHAR'
				elif choice == '4':
					command = 'TRAC'

				self.handler.serve(command)

			elif choice == 'q':

				self.handler.serve('LOGO')
				if LocalData.tracker_is_empty():
					break
				else:
					choice = ''
					continue

			elif choice != 'q':
				shell_colors.print_red('Input code is wrong. Choose one action!\n')

		# waiting 60s for any upload running
		spinner = SpinnerThread('Waiting for any upload in progress', '')
		spinner.start()

		timer = Timer(60, lambda: (self.server.stop(), spinner.stop()))
		timer.start()

		timer.join()
		spinner.join()

		shell_colors.print_blue('\nYou leaved the Network\nBye!\n')
