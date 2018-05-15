#!/usr/bin/env python


from utils import hasher, net_utils
from peer.LocalData import LocalData
from utils import shell_colors as shell
from utils.Downloader import Downloader
import os
import io
import socket


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
			pass

		elif choice == "ADDR":
			# check if shared directory exist
			if not os.path.exists('shared'):
				shell.print_red('\nCannot find the shared folder.')
				return

			# check for file available in shared directory
			if not os.scandir('shared'):
				shell.print_yellow('No file available for sharing. Add files to shared dir to get started.\n')
				return

			temp_files = []
			shell.print_blue('\nFiles available for sharing:')
			for count, file in enumerate(os.scandir('shared'), 1):
				# print scandir results
				file_md5 = hasher.get_md5(f'shared/{file.name}')
				print(f'{count}] {file.name} | {file_md5}')
				temp_files.append((file_md5, file.name))

			while True:
				index = input('Choose a file to share (q to cancel): ')

				if index == "q":
					print('\n')
					return

				try:
					index = int(index) - 1
				except ValueError:
					shell.print_red(f'\nWrong index: number in range 1 - {len(temp_files)} expected\n')
					continue

				if 0 <= index <= len(temp_files):
					file_name = LocalData.get_shared_file_name(temp_files[index])
					file_md5 = LocalData.get_shared_file_md5(temp_files[index])

					# check if file is already in sharing
					if not LocalData.is_shared_file(file_md5, file_name):

						try:
							f_obj = open('shared/' + file_name, 'rb')
						except OSError as e:
							shell.print_red(f'Cannot open the file to upload: {e}')
							return

						try:
							filesize = os.fstat(f_obj.fileno()).st_size
						except OSError as e:
							shell.print_red(f'Something went wrong: {e}')
							raise e

						part_size = str(net_utils.get_part_size())

						# build packet and sent to tracker
						packet = choice + ssid + filesize + part_size + file_md5 + file_name.ljust(100)

						sd = None
						try:
							sd = net_utils.send_packet(tracker_ip4, tracker_ip6, tracker_port, packet)
							shell.print_green(f'Packet sent to tracker: {tracker_ip4}|{tracker_ip6} [{tracker_port}]')
						except net_utils.socket.error:
							shell.print_red(f'\nError while sending packet to tracker: {tracker_ip4}|{tracker_ip6} [{tracker_port}]\n')
							sd.close()

						try:
							response = sd.recv(200).decode()
						except socket.error as e:
							shell.print_red(f'Unable to read the response from the socket: {e}\n')
							sd.close()
							return
						sd.close()

						if len(response) != 12:
							shell.print_red(
								f"Invalid response: : {command} -> {response}. Expected: AADR<num_part>")
							return

						command = response[0:4]

						if command != 'AADR':
							shell.print_red(f"\nInvalid response: {command} -> {response}\n")
							return

						# TODO l'utilizzo di questa num part al momento mi sfugge, quindi la lascio qui pendente in attesa di sviluppi
						num_part = response[4:12]

						# add file to shared_files
						LocalData.add_shared_file(file_md5, file_name)
						shell.print_blue(f'\nNew shared file added {file_name} | {file_md5}', end='')
						shell.print_green(f' \#parts: {num_part}')
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

			sd = net_utils.send_packet(tracker_ip4, tracker_ip6, tracker_port, packet)

			try:
				response = sd.recv(50).decode()
			except socket.error as e:
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
				shell.print_yellow(f'\nUnable to logout:\nYou have {part_down} parts not shared with other peer.\n')

			else:
				shell.print_red(f'\nError while receiving the response for "{choice}".')
				shell.print_red(f'Received from the socket: {command} -> {response}')

		else:
			shell.print_yellow(f'\nInvalid input code: "{choice}".\nPlease retry.\n')
			return
