#!/usr/bin/env python

import socket
import io
import math
from utils import Logger
from utils import net_utils


class Uploader:

	def __init__(self, sd: socket.socket, f_obj: io.FileIO, num_part: int, log: Logger.Logger):
		self.sd = sd
		self.f_obj = f_obj
		self.num_part = num_part
		self.log = log

	def start(self) -> None:
		""" Start file upload

		:return: None
		"""

		part_size = net_utils.config['part_size']

		# move the reading seek to the correct position in the file
		self.f_obj.seek(self.num_part * part_size)

		# read selected the part
		part = self.f_obj.read(part_size)

		# Redef the part size because in case the read part is the last part_size != len(part)
		part_size = len(part)

		# Defining the number of chunks in a part
		nchunk = int(math.ceil(part_size / 4096))

		# Sending the number of chunks to the peer
		response = "AREP" + str(nchunk).zfill(6)
		self.sd.send(response.encode())

		for i in range(nchunk):
			chunk = part[(i*4096):((i+1)*4096)]
			# print(f'Letti {len(data)} bytes da file: {data}')
			read_size = str(len(chunk)).zfill(5)
			self.sd.send(read_size.encode())
			self.sd.send(chunk)
		self.f_obj.close()
