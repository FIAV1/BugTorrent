#!/usr/bin/env python

import socket
import random
from peer.LocalData import LocalData
from utils import Logger
from peer.thread import progress_bar


def __create_socket() -> (socket.socket, int):
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


def __connect(ip4_peer: str, ip6_peer: str, port_peer: int, packet: str) -> socket.socket:
	""" Send the packet to the specified host
	:param ip4_peer: host's ipv4 address
	:param ip6_peer: host's ipv6 address
	:param port_peer: host's port
	:param packet: packet to be sent
	:return: sock: the socket which will receive the response
	"""
	sock, version = __create_socket()

	if version == 4:
		sock.connect((ip4_peer, port_peer))
	else:
		sock.connect((ip6_peer, port_peer))

	sock.send(packet.encode())

	return sock


def run(file_md5: str, file_name: str, part_num: int, part_length: int, total_file_parts: int, log: Logger.Logger):

	owner = LocalData.get_owner_by_part(part_num)
	owner_ip4 = owner[0]
	owner_ip6 = owner[1]
	owner_port = int(owner[2])

	try:
		packet = 'RETP' + file_md5 + str(part_num).zfill(8)

		sock = __connect(owner_ip4, owner_ip6, owner_port, packet)
	except socket.error as e:
		log.write_red(f'\nImpossible to send data to {owner_ip4}|{owner_ip6} [{owner_port}]: {e}\n')
		return

	ack = sock.recv(4).decode()
	if ack != "AREP":
		log.write_red(f'Invalid command received: {ack}. Expected: AREP')
		sock.close()
		return

	try:
		total_chunks = int(sock.recv(6).decode())
	except ValueError:
		log.write_red('Impossible to retrieve the part. Trying later.')
		return

	f_obj = open(f'shared/{file_name}', 'r+b')
	f_obj.seek(part_num * part_length)

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
		f_obj.write(data)

	f_obj.close()

	try:
		packet = 'RPAD' + LocalData.session_id + file_md5 + str(part_num).zfill(8)

		sock = __connect(LocalData.get_tracker_ip4(), LocalData.get_tracker_ip6(), LocalData.get_tracker_port(), packet)
	except socket.error as e:
		log.write_red(f'\nImpossible to send data to {owner_ip4}|{owner_ip6} [{owner_port}]: {e}\n')
		return

	ack = sock.recv(4).decode()
	if ack != "APAD":
		log.write_red(f'\nInvalid command received: {ack}. Expected: APAD\n')
		sock.close()
		return

	try:
		num_parts_owned = int(sock.recv(8).decode())
	except ValueError:
		log.write_red('Error while retrieving the parts owned from the tracker.')
		return

	LocalData.update_downloading_part_list(part_num)
	LocalData.set_num_parts_owned(num_parts_owned)
	progress_bar.print_progress_bar(num_parts_owned, total_file_parts, prefix='Downloading:', suffix='Complete', length=50)
