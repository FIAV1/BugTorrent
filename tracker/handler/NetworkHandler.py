#!/usr/bin/env python

import socket
import ipaddress
import uuid
import math
from common.HandlerInterface import HandlerInterface
from utils import Logger, binary_utils
from tracker.database import database
from tracker.model.Peer import Peer
from tracker.model.File import File
from tracker.model import peer_repository, file_repository
from threading import Lock


class NetworkHandler(HandlerInterface):
	part_list_mutex = Lock()

	def __init__(self, db_file: str, log: Logger.Logger):
		self.db_file = db_file
		self.log = log

	def send_packet(self, sd: socket.socket, ip: str, port: int, packet: str):
		try:
			sd.send(packet.encode())
			sd.close()
			self.log.write_blue(f'Sending to {ip} [{port}] -> ', end='')
			self.log.write(f'{packet}')
		except socket.error as e:
			self.log.write_red(f'An error has occurred while sending {packet} to {ip} [{port}]: {e}')

	def check_peer_authentication(self, conn: database.sqlite3.Connection, session_id: str, sd: socket.socket):
		# authentication check
		peer = peer_repository.find(conn, session_id)

		if peer is None:
			conn.close()
			sd.close()
			self.log.write_red('Unauthorized request received: SessionID is invalid')
			return

		return peer

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

		if command == "LOGI":
			error_response = "ALGI" + '0' * 16

			if len(packet) != 64:
				self.log.write_red(f'Invalid packet received: {packet}')
				self.send_packet(sd, socket_ip_sender, socket_port_sender, error_response)
				return

			ip = packet[4:59]
			port = packet[59:64]

			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row
			except database.Error as e:
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				self.send_packet(sd, socket_ip_sender, socket_port_sender, error_response)
				return

			try:
				peer = peer_repository.find_by_ip(conn, ip)

				# if the peer didn't already logged in
				if peer is None:
					session_id = str(uuid.uuid4().hex[:16].upper())
					peer = peer_repository.find(conn, session_id)

					# while the generated session_id exists
					while peer is not None:
						session_id = str(uuid.uuid4().hex[:16].upper())
						peer = peer_repository.find(conn, session_id)

					peer = Peer(session_id, ip, port)
					peer.insert(conn)

				conn.commit()
				conn.close()
			except database.Error as e:
				conn.rollback()
				conn.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				self.send_packet(sd, socket_ip_sender, socket_port_sender, error_response)
				return

			# the peer is now logged, sending the acknowledge
			response = "ALGI" + peer.session_id
			self.send_packet(sd, socket_ip_sender, socket_port_sender, response)

		elif command == "ADDR":
			if len(packet) != 168:
				sd.close()
				self.log.write_red(f'Invalid packet received: {packet}')
				return

			session_id = packet[4:20]
			try:
				len_file = int(packet[20:30])
				len_part = int(packet[30:36])
			except ValueError:
				sd.close()
				self.log.write_red(f'Invalid packet received: {packet[20:30]} and {packet[30:36]} must be integer.')
				return
			name = packet[36:136].lstrip().rstrip().lower()
			md5 = packet[136:168]

			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row
			except database.Error as e:
				sd.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			try:
				self.check_peer_authentication(conn, session_id, sd)

				file = file_repository.find(conn, md5)

				if file is None:
					file = File(md5, name, len_file, len_part)
					file.insert(conn)

					num_part = int(math.ceil(len_file / len_part))
					part_list_length = int(math.ceil(num_part/8))
					part_list = bytearray(part_list_length)

					for i in range(part_list_length - 1):
						part_list[i] = 255
					for i in range(num_part % 8):
						part_list[part_list_length - 1] |= pow(2, 7-i)

					file_repository.add_owner(conn, md5, session_id, part_list, 1)
				else:
					# the peer already added the file in the past, so i just need to rename it
					file.file_name = name
					file.update(conn)
					num_part = int(math.ceil(file.len_file / file.len_part))

				conn.commit()
				conn.close()
			except database.Error as e:
				conn.rollback()
				conn.close()
				sd.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			# file inserted, sending the acknowledge
			response = "AADR" + str(num_part).zfill(8)
			self.send_packet(sd, socket_ip_sender, socket_port_sender, response)

		elif command == "LOOK":
			if len(packet) != 40:
				sd.close()
				self.log.write_red(f'Invalid packet received: {packet}')
				return

			session_id = packet[4:20]
			query = packet[20:40].lstrip().rstrip().lower()

			if query != '*':
				query = '%' + query + '%'

			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row
			except database.Error as e:
				sd.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			try:
				self.check_peer_authentication(conn, session_id, sd)

				num_files = file_repository.get_files_count_by_querystring(conn, query)

				response = "ALOO" + str(num_files).zfill(3)

				file_rows = file_repository.get_files_by_querystring(conn, query)

				for file_row in file_rows:
					file_md5 = file_row['file_md5']
					file_name = file_row['file_name']
					len_file = file_row['len_file']
					len_part = file_row['len_part']

					response += file_md5 + file_name.ljust(100) + str(len_file).zfill(10) + str(len_part).zfill(6)

				conn.commit()
				conn.close()
			except database.Error as e:
				conn.rollback()
				conn.close()
				sd.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			self.send_packet(sd, socket_ip_sender, socket_port_sender, response)

		elif command == "FCHU":
			if len(packet) != 52:
				sd.close()
				self.log.write_red(f'Invalid packet received: {packet}')
				return

			session_id = packet[4:20]
			file_md5 = packet[20:52]

			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row
			except database.Error as e:
				sd.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			try:
				self.check_peer_authentication(conn, session_id, sd)

				num_hit_peer = file_repository.get_file_owners_count_by_filemd5(conn, file_md5)

				response = "AFCH".encode() + str(num_hit_peer).zfill(3).encode()

				part_list_rows = file_repository.get_all_part_lists_with_owner_by_filemd5(conn, file_md5)

				for part_list_row in part_list_rows:
					owner_ip = part_list_row['ip']
					owner_port = part_list_row['port']
					part_list = part_list_row['part_list']

					response += owner_ip.encode() + owner_port.encode() + part_list

				conn.commit()
				conn.close()
			except database.Error as e:
				conn.rollback()
				conn.close()
				sd.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			try:
				sd.send(response)
				sd.close()
				self.log.write_blue(f'Sending to {socket_ip_sender} [{socket_port_sender}] -> ', end='')
				self.log.write(f'{response}')
			except socket.error as e:
				self.log.write_red(f'An error has occurred while sending {packet} to {socket_ip_sender} [{socket_port_sender}]: {e}')

		elif command == "RPAD":
			if len(packet) != 60:
				sd.close()
				self.log.write_red(f'Invalid packet received: {packet}')
				return

			session_id = packet[4:20]
			file_md5 = packet[20:52]
			try:
				part_num = int(packet[52:60])
			except ValueError:
				sd.close()
				self.log.write_red(f'Invalid packet received: {packet[52:60]} must be integer.')
				return

			# Start update part_list transaction
			NetworkHandler.part_list_mutex.acquire()
			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row
			except database.Error as e:
				NetworkHandler.part_list_mutex.release()
				sd.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			try:
				self.check_peer_authentication(conn, session_id, sd)
				new_part_list = False
				part_list = file_repository.get_part_list_by_file_and_owner(conn, file_md5, session_id)

				if not part_list:
					new_part_list = True
					# create an empty part list
					generic_part_list = file_repository.get_part_list_by_filemd5(conn, file_md5)
					part_list = bytearray(len(generic_part_list))
				else:
					part_list = bytearray(part_list)

				# calc the index of the list that must be updated
				byte_index = int(math.floor(part_num / 8))
				# calc the position of the bit to toggle
				bit_index = part_num % 8
				# update the part list
				part_list[byte_index] |= pow(2, 7 - bit_index)

				if new_part_list:
					file_repository.add_owner(conn, file_md5, session_id, part_list, 0)
				else:
					file_repository.update_part_list_by_file_and_owner(conn, file_md5, session_id, part_list)

				conn.commit()
				conn.close()
				NetworkHandler.part_list_mutex.release()
			except database.Error as e:
				conn.rollback()
				conn.close()
				NetworkHandler.part_list_mutex.release()
				sd.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			num_owned_parts = 0
			for part in part_list:
				num_owned_parts += binary_utils.count_set_bits(part)

			response = "APAD" + str(num_owned_parts).zfill(8)
			self.send_packet(sd, socket_ip_sender, socket_port_sender, response)

		elif command == "LOGO":
			if len(packet) != 20:
				sd.close()
				self.log.write_red(f'Invalid packet received: {packet}')
				return

			session_id = packet[4:20]
			can_logout = True

			try:
				conn = database.get_connection(self.db_file)
				conn.row_factory = database.sqlite3.Row
			except database.Error as e:
				sd.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			try:
				peer = self.check_peer_authentication(conn, session_id, sd)

				# logout permission check
				peer_files = file_repository.get_peer_files(conn, session_id, 1)

				for file_row in peer_files:
					file_md5 = file_row['file_md5']
					len_file = file_row['len_file']
					len_part = file_row['len_part']

					num_part = int(math.ceil(len_file / len_part))
					part_list_length = int(math.ceil(num_part / 8))

					NetworkHandler.part_list_mutex.acquire()
					part_list_rows = file_repository.get_all_part_lists_by_file_excluding_owner(conn, file_md5, session_id)
					owner_part_list = file_repository.get_part_list_by_file_and_owner(conn, file_md5, session_id)
					part_list_element_mask = 0

					for i in range(part_list_length):
						# i help us get every i-th item of every part lists
						for part_list_row in part_list_rows:
							part_list = bytearray(part_list_row['part_list'])
							part_list_element_mask |= part_list[i]

						if part_list_element_mask != owner_part_list[i]:
							can_logout = False
							break

						part_list_element_mask = 0

					if not can_logout:
						break

				# response management
				if can_logout:
					num_part_own = 0
					# get all the parts owned by the peer
					part_list_rows = file_repository.get_peer_part_lists(conn, session_id)
					for part_list_row in part_list_rows:
						num_part_own += binary_utils.count_set_bits(int.from_bytes(part_list_row['part_list'], 'big'))

					file_repository.delete_peer_files(conn, session_id)
					peer.delete(conn)

					response = "ALOG" + str(num_part_own).zfill(10)
				else:
					num_part_down = 0
					# get the parts amount downloaded by the network
					for file_row in peer_files:
						file_md5 = file_row['file_md5']
						len_file = file_row['len_file']
						len_part = file_row['len_part']

						num_part = int(math.ceil(len_file / len_part))
						part_list_length = int(math.ceil(num_part / 8))

						part_list_rows = file_repository.get_all_part_lists_by_file_excluding_owner(conn, file_md5, session_id)
						part_list_element_mask = 0

						for i in range(part_list_length):
							# i help us get every i-th item of every part lists
							for part_list_row in part_list_rows:
								part_list = bytearray(part_list_row['part_list'])
								part_list_element_mask |= part_list[i]

							num_part_down += binary_utils.count_set_bits(part_list_element_mask)
							part_list_element_mask = 0

					response = "NLOG" + str(num_part_down).zfill(10)

				conn.commit()
				conn.close()
				NetworkHandler.part_list_mutex.release()
			except database.Error as e:
				conn.rollback()
				conn.close()
				NetworkHandler.part_list_mutex.release()
				sd.close()
				self.log.write_red(f'An error has occurred while trying to serve the request: {e}')
				return

			self.send_packet(sd, socket_ip_sender, socket_port_sender, response)

		else:
			sd.close()
			self.log.write_red(f'Invalid packet received from {socket_ip_sender} [{socket_port_sender}]: ', end='')
			self.log.write(f'{packet}')

		return
