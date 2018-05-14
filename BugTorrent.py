from utils import shell_colors as shell

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


choice = ''
while choice != 'q':
	choice = input('\nHi! Welcome to BugTorrent (q to exit): ')
	if choice == 'y':
		print('u mom gay')
		break
	elif choice == 'n':
		print('no u')
		break
	else:
		shell.print_red('Both ur moms r gay\n')
