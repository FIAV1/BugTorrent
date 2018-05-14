#!/usr/bin/env python

from utils import net_utils, hasher, shell_colors as shell
from utils.Downloader import Downloader
import uuid
import os
import socket
from superpeer.LocalData import LocalData
from common.ServerThread import ServerThread
from .MenuTimedResponseHandler import MenuTimedResponseHandler
from utils.SpinnerThread import SpinnerThread
from threading import Timer
from superpeer.database import database
from superpeer.model import file_repository, peer_repository

db_file = 'superpeer/database/directory.db'


class MenuHandler:

	def serve(self, choice: str) -> None:
		""" Handle the peer packet

		:param choice: the choice to handle
		:return: None
		"""

		if choice == "":
			pass

		elif choice == "":
			pass

		else:
			pass
