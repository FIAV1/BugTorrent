#!/usr/bin/env python

from threading import Thread, Event
import time
import socket
import random
from peer.LocalData import LocalData
from utils import Logger
from utils import net_utils


class UpdaterThread(Thread):
	def __init__(self, file_md5: str, part_list_length: int, update_event: Event, log: Logger.Logger):
		super(UpdaterThread, self).__init__()
		self.__stop_event = Event()
		self.file_md5 = file_md5
		self.part_list_length = part_list_length
		self.update_event = update_event
		self.log = log

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

	def run(self):
		tracker_ip4 = LocalData.get_tracker_ip4()
		tracker_ip6 = LocalData.get_tracker_ip6()
		tracker_port = LocalData.get_tracker_port()
		session_id = LocalData.get_session_id()

		while not self.__stop_event.is_set():
			try:
				packet = 'FCHU' + session_id + self.file_md5

				sock = self.__connect(tracker_ip4, tracker_ip6, tracker_port, packet)
			except socket.error as e:
				self.log.write_red(f'\nImpossible to send data to {tracker_ip4}|{tracker_ip6} [{tracker_port}]: {e}\n')
				break

			ack = sock.recv(4).decode()
			if ack != "AFCH":
				self.log.write_red(f'\nInvalid command received: {ack}. Expected: AFCH\n')
				sock.close()
				break

			num_hitpeer = int(sock.recv(3).decode())

			part_list_table = list()
			for i in range(num_hitpeer):
				(hitpeer_ip4, hitpeer_ip6) = net_utils.get_ip_pair(sock.recv(55).decode())
				hitpeer_port = sock.recv(5).decode()
				part_list = sock.recv(self.part_list_length)

				# Adding only other peers to the part list table regarding the file of interest
				if hitpeer_ip4 != net_utils.get_local_ipv4() and hitpeer_ip6 != net_utils.get_local_ipv6():
					part_list_table.append(((hitpeer_ip4, hitpeer_ip6, hitpeer_port), bytearray(part_list)))

			LocalData.set_part_list_table(part_list_table)

			self.log.write(f'\nPart list table for ', end='')
			self.log.write_yellow(f'{self.file_md5} ', end='')
			self.log.write(f'updated: ', end='')
			self.log.write_green(f'{len(part_list_table)} ', end='')
			self.log.write(f'sources added:')
			for source in part_list_table:
				self.log.write_blue(f'{source[0][0]}|{source[0][1]} [{source[0][2]}]')
			self.log.write('')

			LocalData.update_downloadable_parts()
			self.log.write_blue(f'Downloadable parts:')
			for part_num in LocalData.get_downloadable_parts():
				self.log.write(f'{str(part_num)}, ', end='')
			self.log.write('')

			self.update_event.set()

			time.sleep(60)

	def stop(self):
		self.__stop_event.set()
