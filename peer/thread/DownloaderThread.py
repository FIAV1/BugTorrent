#!/usr/bin/env python

import socket
import random
import io
from peer.LocalData import LocalData
from utils import shell_colors
from threading import Thread
from peer.thread import progress_bar


class DownloaderThread(Thread):

	def __init__(self, owner: tuple, file_md5: str, f_obj: io.FileIO, part_num: int, total_file_parts: int):
		super(DownloaderThread, self).__init__()
		self.owner_ip4 = owner[0]
		self.owner_ip6 = owner[1]
		self.owner_port = int(owner[2])
		self.file_md5 = file_md5
		self.f_obj = f_obj
		self.part_num = part_num
		self.total_file_parts = total_file_parts


	def __create_socket(self) -> (socket.socket, int):
		""" Create the active socket
		:return: the active socket and the version
		"""
		# Create the socket
		if random.random() <= 0.5:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			version = 4
		else:
			sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			version = 6

		return sock, version

	def __connect(self, ip4_peer: str, ip6_peer: str, port_peer: int, packet: str) -> socket.socket:
		""" Send the packet to the specified host
		:param ip4_peer: host's ipv4 address
		:param ip6_peer: host's ipv6 address
		:param port_peer: host's port
		:param packet: packet to be sent
		:return: sock: the socket which will receive the response
		"""
		sock, version = self.__create_socket()

		if version == 4:
			sock.connect((ip4_peer, port_peer))
		else:
			sock.connect((ip6_peer, port_peer))

		sock.send(packet.encode())

		return sock

	def run(self) -> None:
		""" Start file download

		:return: None
		"""

		try:
			packet = 'RETP' + self.file_md5 + str(self.part_num).zfill(8)

			sock = self.__connect(self.owner_ip4, self.owner_ip6, self.owner_port, packet)
		except socket.error as e:
			shell_colors.print_red(f'\nImpossible to send data to {self.owner_ip4}|{self.owner_ip6} [{self.owner_port}]: {e}\n')
			return

		ack = sock.recv(4).decode()
		if ack != "AREP":
			shell_colors.print_red(f'Invalid command received: {ack}. Expected: AREP')
			sock.close()
			return

		try:
			total_chunks = int(sock.recv(6).decode())
		except ValueError:
			shell_colors.print_red('Impossible to retrieve the part. Trying later.')
			return

		for i in range(total_chunks):
			chunk_size = sock.recv(5)
			# if not all the 5 expected bytes has been received
			while len(chunk_size) < 5:
				chunk_size += sock.recv(1)
			chunk_size = int(chunk_size)

			data = sock.recv(chunk_size)
			# if not all the expected bytes has been received
			while len(data) < chunk_size:
				data += sock.recv(1)
			self.f_obj.write(data)

		self.f_obj.close()

		try:
			packet = 'RPAD' + LocalData.session_id + self.file_md5 + str(self.part_num).zfill(8)

			sock = self.__connect(LocalData.get_tracker_ip4(), LocalData.get_tracker_ip6(), LocalData.get_tracker_port(), packet)
		except socket.error as e:
			shell_colors.print_red(f'\nImpossible to send data to {self.owner_ip4}|{self.owner_ip6} [{self.owner_port}]: {e}\n')
			return

		ack = sock.recv(4).decode()
		if ack != "APAD":
			shell_colors.print_red(f'\nInvalid command received: {ack}. Expected: APAD\n')
			sock.close()
			return

		try:
			num_parts_owned = int(sock.recv(8).decode())
		except ValueError:
			shell_colors.print_red('Error while retrieving the parts owned from the tracker.')
			return

		binary_utils.update_owned_parts(self.part_num)
		LocalData.set_num_parts_owned(num_parts_owned)
		progress_bar.print_progress_bar(num_parts_owned, self.total_file_parts, prefix='Downloading:', suffix='Complete', length=50)
