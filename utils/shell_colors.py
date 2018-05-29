#!/usr/bin/env python

DEFAULTBG = '\033[49m'
RESET = '\033[0m'
BOLD = '\033[1m'
UNDERLINED = '\033[4m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
PURPLE = '\033[35m'


def print_red(string, end='\n'):
	print(DEFAULTBG + BOLD + RED + string + RESET, end=end)


def print_blue(string, end='\n'):
	print(DEFAULTBG + BOLD + BLUE + string + RESET, end=end)


def print_green(string, end='\n'):
	print(DEFAULTBG + BOLD + GREEN + string + RESET, end=end)


def print_yellow(string, end='\n'):
	print(DEFAULTBG + BOLD + YELLOW + string + RESET, end=end)


def print_purple(string, end='\n'):
	print(DEFAULTBG + BOLD + PURPLE + string + RESET, end=end)
