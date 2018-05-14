import os
from utils import net_utils, shell_colors as shell
from peer import peer
from tracker import tracker

shell.print_purple(	"__________", end="")
shell.print_green(	"           ___________                                 __")
shell.print_purple(	"\______   \__ __  ___", end="")
shell.print_green(	"\__    ___/_________________   ____   _____/  |_")
shell.print_purple(	" |    |  _/  |  \/ ___\\", end="")
shell.print_green(	"|    | /  _ \_  __ \_  __ \_/ __ \ /    \   __\\")
shell.print_purple(	" |    |   \  |  / /_/  >", end="")
shell.print_green(	"    |(  <_> )  | \/|  | \/\  ___/|   |  \  |")
shell.print_purple(	" |______  /____/\___  /", end="")
shell.print_green(	"|____| \____/|__|   |__|    \___  >___|  /__|")
shell.print_purple(	"        \/     /_____/", end="")
shell.print_green(	"                                 \/     \/")

if not os.path.exists('shared'):
	os.mkdir('shared')

net_utils.prompt_parameters_request()

choice = ''
while choice != 'q':
	choice = input('\nAre you a tracker? (y/n): ')
	if choice == 'y':
		tracker.startup()
		break
	elif choice == 'n':
		peer.startup()
		break
	else:
		shell.print_red('Input code is wrong. Choose y or n!\n')
