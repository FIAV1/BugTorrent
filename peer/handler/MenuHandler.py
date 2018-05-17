#!/usr/bin/env python

from utils import hasher, net_utils
from peer.LocalData import LocalData
from utils import shell_colors as shell
from peer.utils.Downloader import Downloader
import os


class MenuHandler:

	@staticmethod
	def serve(choice: str) -> None:
		""" Handle the peer packet

		:param choice: the choice to handle
		:return: None
		"""

		tracker_ip4 = LocalData.get_tracker_ip4()
		tracker_ip6 = LocalData.get_tracker_ip6()
		tracker_port = LocalData.get_tracker_port()
		ssid = LocalData.get_session_id()

		if choice == "LOOK":
			while True:
				search = input('\nInsert file\'s name (q to cancel): ')

				if search == "q":
					print('\n')
					return

				if not 0 < len(search) <= 20:
					shell.print_red('\nQuery string must be a valid value (1 - 20 chars).')
					continue

				break

			packet = choice + ssid + search.ljust(20)

			sd = None
			try:
				sd = net_utils.send_packet(tracker_ip4, tracker_ip6, tracker_port, packet)
			except net_utils.socket.error as e:
				shell.print_red(
					f'\nError while sending the request to the tracker: {tracker_ip4}|{tracker_ip6} [{tracker_port}].')
				shell.print_red(f'Error: {e}')
				if sd is not None:
					sd.close()
				return

			try:
				command = sd.recv(4).decode()
			except net_utils.socket.error as e:
				shell.print_red(f'Unable to read the command from the socket: {e}\n')
				sd.close()
				return

			if command != 'ALOO':
				shell.print_red(f'\nReceived a packet with a wrong command ({command}).')
				return

			try:
				num_files = int(sd.recv(3).decode())
			except net_utils.socket.error as e:
				shell.print_red(f'Unable to read the command from the socket: {e}\n')
				sd.close()
				return

			# check for file matching the keyword
			if num_files == 0:
				shell.print_yellow(f'{search} not found.\n')
				sd.close()
				return

			downloadables = list()

			for i in range(num_files):

				try:
					file_md5 = sd.recv(32).decode()
					file_name = sd.recv(100).decode().lstrip().rstrip()
					len_file = int(sd.recv(10))
					len_part = int(sd.recv(6))
				except net_utils.socket.error as e:
					shell.print_red(f'\nError while receiving the response from the tracker: {e}\n')
					continue
				except ValueError:
					shell.print_red(f'\nInvalid packet from tracker: {e}\n')
					continue

				downloadables.append((file_md5, file_name, len_file, len_part))

			sd.close()

			if not downloadables:
				shell.print_red(f'\nSomething went wrong while retrieving {search}\n')
				return

			shell.print_green(f'\nFiles found:')
			for count, downloadable in enumerate(downloadables, 1):
				print(f'{count}] {LocalData.get_downloadable_file_name(downloadable)} | ', end='')
				shell.print_yellow(f'{LocalData.get_downloadable_file_md5(downloadable)}')

			while True:
				file_index = input('Choose a file to download (q to cancel): ')

				if file_index == "q":
					print('\n')
					return

				try:
					file_index = int(file_index) - 1
				except ValueError:
					shell.print_red(f'\nWrong index: number in range 1 - {len(downloadables)} expected\n')
					continue

				if not 0 <= file_index <= len(downloadables) - 1:
					shell.print_red(f'\nWrong index: number in range 1 - {len(downloadables)} expected\n')
					continue
				else:
					choosed_file_md5 = LocalData.get_downloadable_file_md5(downloadables[file_index])
					choosed_file_name = LocalData.get_downloadable_file_name(downloadables[file_index])
					choosed_file_lenght = LocalData.get_downloadable_file_length(downloadables[file_index])
					choosed_file_part_lenght = LocalData.get_downloadable_file_part_length(downloadables[file_index])

				try:
					Downloader(choosed_file_md5, choosed_file_name, choosed_file_lenght, choosed_file_part_lenght).start()
				except OSError:
					shell.print_red(f'\nError while downloading {choosed_file_name}.\n')
				break

		elif choice == "ADDR":
			# check if shared directory exist
			if not os.path.exists('shared'):
				shell.print_red('\nCannot find the shared folder.')
				return

			# check for file available in shared directory
			if not os.listdir('shared'):
				shell.print_yellow('No file available for sharing.\nAdd files to shared dir to get started.\n')
				return

			temp_files = []
			shell.print_blue('\nFiles available for sharing:')
			for count, file in enumerate(os.scandir('shared'), 1):
				# print scandir results
				file_md5 = hasher.get_md5(f'shared/{file.name}')
				print(f'{count}] {file.name} | {file_md5}')
				temp_files.append((file_md5, file.name))

			while True:
				file_index = input('Choose a file to share (q to cancel): ')

				if file_index == "q":
					print('\n')
					return

				try:
					file_index = int(file_index) - 1
				except ValueError:
					shell.print_red(f'\nWrong index: number in range 1 - {len(temp_files)} expected\n')
					continue

				if 0 <= file_index <= len(temp_files) - 1:
					file_name = LocalData.get_shared_file_name(temp_files[file_index])
					file_md5 = LocalData.get_shared_file_md5(temp_files[file_index])

					# check if file is already in sharing
					if not LocalData.is_shared_file(file_md5, file_name):

						try:
							f_obj = open('shared/' + file_name, 'rb')
						except OSError as e:
							shell.print_red(f'Cannot open the file to upload: {e}')
							return

						try:
							filesize = str(os.fstat(f_obj.fileno()).st_size)
						except OSError as e:
							shell.print_red(f'Something went wrong: {e}')
							return
						except ValueError as e:
							shell.print_red(f'\nUnable to convert filesize in string: {e}\n')
							return

						part_size = str(net_utils.get_part_size())

						# build packet and sent to tracker
						packet = choice + ssid + filesize.zfill(10) + part_size.zfill(6) + file_name.ljust(100) + file_md5

						sd = None
						try:
							sd = net_utils.send_packet(tracker_ip4, tracker_ip6, tracker_port, packet)
						except net_utils.socket.error as e:
							shell.print_red(
								f'\nError while sending the request to the tracker: {tracker_ip4}|{tracker_ip6} [{tracker_port}].')
							shell.print_red(f'Error: {e}')
							if sd is not None:
								sd.close()
							return

						try:
							response = sd.recv(200).decode()
						except net_utils.socket.error as e:
							shell.print_red(f'Unable to read the response from the socket: {e}\n')
							sd.close()
							return
						sd.close()

						if len(response) != 12:
							shell.print_red(
								f"Invalid response: : {response}. Expected: AADR<num_part>")
							return

						command = response[0:4]

						if command != 'AADR':
							shell.print_red(f'\nReceived a packet with a wrong command ({command}).')
							return

						# TODO l'utilizzo di questa num part al momento mi sfugge, quindi la lascio qui pendente in attesa di sviluppi
						num_part = response[4:12]

						# add file to shared_files
						LocalData.add_shared_file(file_md5, file_name)
						shell.print_blue(f'\nNew shared file added {file_name} | {file_md5}', end='')
						shell.print_green(f' #parts: {num_part}')
						break
					else:
						# if not in sharing
						shell.print_yellow(f'\n{file_name} | {file_md5} already in sharing.\n')
						break
				else:
					shell.print_red(f'\nWrong index: number in range 1 - {len(temp_files)} expected\n')
					continue

		elif choice == "LOGO":
			packet = choice + ssid

			sd = None
			try:
				sd = net_utils.send_packet(tracker_ip4, tracker_ip6, tracker_port, packet)
			except net_utils.socket.error as e:
				shell.print_red(
					f'\nError while sending the request to the tracker: {tracker_ip4}|{tracker_ip6} [{tracker_port}].')
				shell.print_red(f'{e}')
				if sd is not None:
					sd.close()
				return

			try:
				response = sd.recv(50).decode()
			except net_utils.socket.error as e:
				shell.print_red(f'Unable to read the response from the socket: {e}\n')
				sd.close()
				return

			sd.close()

			if len(response) != 14:
				shell.print_red(f"Invalid response form the socket: {response}.")
				return

			command = response[0:4]

			if command == "ALOG":
				part_own = int(response[4:13])
				shell.print_green('\nSuccessfully logged out')
				shell.print_blue(f'{part_own} parts has been removed from sharing.\n')
				LocalData.clear_shared_files()
				LocalData.clear_tracker()

			elif command == "NLOG":
				part_down = int(response[4:13])
				shell.print_yellow(f'\nUnable to logout:\nYou have shared only {part_down} parts with other peer.\n')

			else:
				shell.print_red(f'\nReceived a packet with a wrong command from the socket: {command} -> {response}')

		else:
			shell.print_yellow(f'\nInvalid input code: "{choice}".\nPlease retry.\n')
			return
