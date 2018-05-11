#!/usr/bin/env python

import time
from threading import Timer
from utils.SpinnerThread import SpinnerThread
from utils import hasher, net_utils
from peer.LocalData import LocalData
from utils import shell_colors as shell
from utils.Downloader import Downloader
import os


class MenuHandler:

	@staticmethod
	def serve(choice: str) -> None:
		""" Handle the peer packet

		:param choice: the choice to handle
		:return: None
		"""
		if choice == "LOOK":
			pass

		elif choice == "ADDR":
			pass

		elif choice == "LOGO":
			pass

		else:
			pass
