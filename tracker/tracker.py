#!/usr/bin/env python

from utils import net_utils, Logger
from common.ServerThread import ServerThread
from .handler import NetworkHandler, MenuHandler
from .Menu import Menu
from tracker.database import database

DB_FILE = 'tracker/database/directory.db'


def startup():

	if not database.exist(DB_FILE):
		database.create_database(DB_FILE)
	else:
		database.reset_database(DB_FILE)

	log = Logger.Logger('tracker/tracker.log')

	server = ServerThread(net_utils.get_tracker_port(), NetworkHandler.NetworkHandler(DB_FILE, log))
	server.daemon = True
	server.start()

	Menu(MenuHandler.MenuHandler(DB_FILE)).show()
