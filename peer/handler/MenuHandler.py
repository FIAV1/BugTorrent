#!/usr/bin/env python


from utils import hasher, net_utils
from peer.LocalData import LocalData
from utils import shell_colors as shell
from utils.Downloader import Downloader
import os
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
				# print scandir's results
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

				if 0 <= index <= len(temp_files)-1:
					file_name = LocalData.get_shared_file_name(temp_files[index])
					file_md5 = LocalData.get_shared_file_md5(temp_files[index])

					# chek if file is already in sharing
					if not LocalData.is_shared_file(temp_files[index]):

						# build packet and sent to tracker
						packet = choice + ssid + file_md5 + file_name.ljust(100)
						try:
							sd = net_utils.send_packet(tracker_ip4, tracker_ip6, tracker_port, packet)
							shell.print_green(f'Packet sent to tracker: {sp_ip4}|{sp_ip6} [{sp_port}]')
						except net_utils.socket.error:
							shell.print_red(f'\nError while sending packet to tracker: {sp_ip4}|{sp_ip6} [{sp_port}]\n')
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

						num_part = response[4:12]

						# add file to shared_files
						LocalData.add_shared_file(file_md5, file_name)
						shell.print_blue(f'\nNew shared file added {file_name} | {file_md5}')
						break
					else:
						# il file è già in condivisione
						shell.print_yellow(f'\n{file_name} | {file_md5} already in sharing.\n')
						break
				else:
					shell.print_red(f'\nWrong index: number in range 1 - {len(temp_files)} expected\n')
					continue

		elif choice == "LOGO":
			pass

		else:
			pass
