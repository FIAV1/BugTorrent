#!/usr/bin/env python

import socket
import ipaddress
from common.HandlerInterface import HandlerInterface
from utils import Logger, shell_colors as shell
from peer.LocalData import LocalData
from peer.utils.Uploader import Uploader


class UploadHandler(HandlerInterface):

	def __init__(self, log: Logger.Logger):
		self.log = log

	def send_packet(self, sd: socket.socket, ip: str, port: int, packet: str):
		try:
			sd.send(packet.encode())
			sd.close()
			self.log.write_blue(f'Sending to {ip} [{port}] -> ', end='')
			self.log.write(f'{packet}')
		except socket.error as e:
			self.log.write_red(f'An error has occurred while sending {packet} to {ip} [{port}]: {e}')

	def serve(self, sd: socket.socket) -> None:
		""" Handle a network packet

		:param sd: the socket descriptor used for read the packet
		:return: None
		"""

		try:
			packet = sd.recv(200).decode()
		except socket.error as e:
			self.log.write_red(f'Unable to read the packet from the socket: {e}')
			sd.close()
			return

		# log the packet received
		socket_ip_sender = sd.getpeername()[0]

		if ipaddress.IPv6Address(socket_ip_sender).ipv4_mapped is None:
			socket_ip_sender = ipaddress.IPv6Address(socket_ip_sender).compressed
		else:
			socket_ip_sender = ipaddress.IPv6Address(socket_ip_sender).ipv4_mapped.compressed

		socket_port_sender = sd.getpeername()[1]

		self.log.write_green(f'{socket_ip_sender} [{socket_port_sender}] -> ', end='')
		self.log.write(f'{packet}')

		command = packet[:4]

		if command == "RETP":

			if len(packet) != 44:
				self.log.write_red(f'Invalid packet received: {packet}')
				return

			file_md5 = packet[4:36]

			try:
				num_part = int(packet[36:44])
			except ValueError:
				shell.print_red(f'Invalid packet received: Part-Num must be an integer -> {num_part}\n')
				return

			file_name = LocalData.get_shared_file_name_from_md5(file_md5)

			if file_name is None:
				error_packet = 'Sorry, the requested file is not available anymore.'
				self.send_packet(sd, socket_ip_sender, socket_port_sender, error_packet)
				sd.close()
				return

			try:
				f_obj = open('shared/' + file_name, 'rb')
			except OSError as e:
				self.log.write_red(f'Cannot open the file to upload: {e}')
				error_packet = 'Sorry, the peer encountered a problem while uploading the file.'
				self.send_packet(sd, socket_ip_sender, socket_port_sender, error_packet)
				sd.close()
				return

			try:
				Uploader(sd, f_obj, num_part, self.log).start()
				self.log.write_blue(f'Sent {socket_ip_sender} [{socket_port_sender}] -> ', end='')
				self.log.write(f'{file_name}')
				sd.close()

			except OSError as e:
				self.log.write_red(f'Error while sending the file: {e}')
				sd.close()
				return

		else:
			sd.close()
			self.log.write_red(f'Invalid packet received from {socket_ip_sender} [{socket_port_sender}]: ', end='')
			self.log.write(f'{packet}')
		return
