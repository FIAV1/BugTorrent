#!/usr/bin/env python

import socket
import os
import io
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
		# TODO questa è solo una prima versione, devo ragionare bene sul comportamento per l'ultima parte,
		# TODO che quasi sicuramente non avrà lunghezza part_size percui il numero di chunks è diverso
		# TODO e dipende dalla dimensione di questa parte --> CALCOLARE IL #PART E VERIFICARE CHE QUELLA RICHIESTA SIA L'ULTIMA??
		part_size = int(net_utils.config['part_size'])

		# Defing the number of chunks in a part
		nchunk = part_size / 4096

		# Verify if the part is exactly divided by the chunks
		if (part_size % 4096) != 0:
			nchunk = nchunk + 1

		nchunk = int(nchunk)

		# Sending the number of chunks to the peer
		response = "ARET" + str(nchunk).zfill(6)
		self.sd.send(response.encode())

		# move the reading seek to the correct position in the file
		self.f_obj.seek(self.num_part*part_size)

		for i in range(nchunk):
			data = self.f_obj.read(4096)
			# print(f'Letti {len(data)} bytes da file: {data}')
			readed_size = str(len(data)).zfill(5)
			self.sd.send(readed_size.encode())
			self.sd.send(data)
		self.f_obj.close()
