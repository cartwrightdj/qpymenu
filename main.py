
import sys
from qpymenu import pyMenu, pyMenuItem, hello_world, read_text_file, about

main_menu = pyMenu("Main Menu",type=pyMenu.Types.HorizontalBar)


# 'File' Menu

file_menu = pyMenu("File", action=lambda: sys.stdout.write("File action executed"), hotkey='F')
file_menu.add_item(pyMenuItem("Hello World", action=hello_world, hotkey='X'))
file_menu.add_item(pyMenuItem("Exit", action=exit, hotkey='X'))


edit_menu = pyMenu("Edit", action=lambda: sys.stdout.write("Edit action executed"), hotkey='E')
edit_menu.add_item(pyMenuItem("Read Text File", action=read_text_file, args="", hotkey='X'))


view_menu = pyMenu("View", action=lambda: sys.stdout.write("View action executed"), hotkey='V')
view_menu.add_item(pyMenuItem("View Item #1", action=lambda: sys.stdout.write("View action1 executed"), hotkey='X'))


help_menu = pyMenu("Help", hotkey='H')
help_menu.add_item(pyMenuItem("View Item #1", action=about, hotkey='X'))


main_menu.add_item(file_menu)
main_menu.add_item(edit_menu)      
main_menu.add_item(view_menu)
main_menu.add_item(help_menu)


#edit_menu.add_item(pyMenuItem("Test Print to StdOut", action=test_print, hotkey='X'))
edit_menu.add_item(pyMenuItem("Item_____2", action=lambda: sys.stdout.write("Edit action3 executed"), hotkey='X'))
mi3 = pyMenu("MenuItem________3", hotkey='X')
mi4 = pyMenu("SubLevel________3", hotkey='X')
edit_menu.add_item(mi3)
mi3.add_item(pyMenuItem("Level2_____1", action=lambda: sys.stdout.write("m3 action1 executed"), hotkey='X'))
mi3.add_item(pyMenuItem("level2_____2", action=lambda: sys.stdout.write("m3 action2 executed"), hotkey='X'))
mi3.add_item(mi4)
mi4.add_item(pyMenuItem("level3_____1", action=lambda: sys.stdout.write("m3 action2 executed"), hotkey='X'))

main_menu.show()