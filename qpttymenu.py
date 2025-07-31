import os
import sys
from collections import OrderedDict
import msvcrt
from typing import Union

# ----------------------------------------------------------------------
# ANSI helper
# ----------------------------------------------------------------------
class Terminal:
    @staticmethod
    def move_to(row: int, col: int):
        # Clamp to 1-based positions
        row = max(1, row)
        col = max(1, col)
        sys.stdout.write(f"\033[{row};{col}H")

    @staticmethod
    def clear_screen():
        sys.stdout.write("\033[2J")

    @staticmethod
    def clear_line():
        sys.stdout.write("\033[2K")

    @staticmethod
    def hide_cursor():
        sys.stdout.write("\033[?25l")

    @staticmethod
    def show_cursor():
        sys.stdout.write("\033[?25h")

    @staticmethod
    def save_cursor():
        sys.stdout.write("\033[s")

    @staticmethod
    def restore_cursor():
        sys.stdout.write("\033[u")

    @staticmethod
    def flush():
        sys.stdout.flush()
    
    @staticmethod
    def clear_region(row: int, col_start: int, col_end: int):
        """
        Clears (overwrites with spaces) the area on `row` between `col_start` and `col_end` (inclusive).
        Coordinates are 1-based.
        """
        width = max(0, col_end - col_start + 1)
        # 1) move cursor to (row, col_start)
        sys.stdout.write(f"\033[{row};{col_start}H")
        # 2) overwrite with spaces
        sys.stdout.write(" " * width)
        # 3) (optional) move cursor back to col_start
        sys.stdout.write(f"\033[{row};{col_start}H")
        sys.stdout.flush()

ansi = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "italic": "\033[3m",
    "underline": "\033[4m",
    "blink": "\033[5m",
    "reverse": "\033[7m",
    "hidden": "\033[8m",
    "strike": "\033[9m",

    # Foreground colors
    "fg_black": "\033[30m",
    "fg_red": "\033[31m",
    "fg_green": "\033[32m",
    "fg_yellow": "\033[33m",
    "fg_blue": "\033[34m",
    "fg_magenta": "\033[35m",
    "fg_cyan": "\033[36m",
    "fg_white": "\033[37m",
    "fg_default": "\033[39m",

    # Bright foreground colors
    "fg_bright_black": "\033[90m",
    "fg_bright_red": "\033[91m",
    "fg_bright_green": "\033[92m",
    "fg_bright_yellow": "\033[93m",
    "fg_bright_blue": "\033[94m",
    "fg_bright_magenta": "\033[95m",
    "fg_bright_cyan": "\033[96m",
    "fg_bright_white": "\033[97m",

    # Background colors
    "bg_black": "\033[40m",
    "bg_red": "\033[41m",
    "bg_green": "\033[42m",
    "bg_yellow": "\033[43m",
    "bg_blue": "\033[44m",
    "bg_magenta": "\033[45m",
    "bg_cyan": "\033[46m",
    "bg_white": "\033[47m",
    "bg_default": "\033[49m",

    # Bright background colors
    "bg_bright_black": "\033[100m",
    "bg_bright_red": "\033[101m",
    "bg_bright_green": "\033[102m",
    "bg_bright_yellow": "\033[103m",
    "bg_bright_blue": "\033[104m",
    "bg_bright_magenta": "\033[105m",
    "bg_bright_cyan": "\033[106m",
    "bg_bright_white": "\033[107m",

    "clear_screen": "\033[2J",
    "clear_line": "\033[2K",
    "cursor_home": "\033[H",
    "cursor_up": "\033[A",
    "cursor_down": "\033[B",
    "cursor_forward": "\033[C",
    "cursor_back": "\033[D",
    "save_cursor": "\033[s",
    "restore_cursor": "\033[u",
    "hide_cursor": "\033[?25l",
    "show_cursor": "\033[?25h",
    "scroll_up": "\033[S",
    "scroll_down": "\033[T",
    "erase_to_end_of_line": "\033[K",
    "erase_to_start_of_line": "\033[1K",
    "erase_entire_line": "\033[2K",
    "erase_to_end_of_screen": "\033[J",
    "erase_to_start_of_screen": "\033[1J",
    "erase_entire_screen": "\033[2J",
}

DOWN_KEY = [b'\x00', b'P']  # Arrow down key code
XDOWN_KEY = [b'\xe0', b'P']  # Arrow down key code
UP_KEY = [b'\x00', b'H']  # Arrow up key code
XUP_KEY = [b'\xe0', b'H']  # Arrow up key code
RIGHT_KEY = [b'\x00', b'M']  # Arrow right key code
XRIGHT_KEY = [b'\xe0', b'M']  # Arrow right key code
LEFT_KEY = [b'\x00', b'K']  # Arrow left key code  
XLEFT_KEY = [b'\xe0', b'K']  # Arrow left key code  
ENTER_KEY = [b'\r']  # Enter key code


class pyMenuStdOut():
    def __init__(self) -> None:
        self.buffer = []
    
    def write(self, text):
        # get terminal size
        size = os.get_terminal_size()
        cols, rows = size.columns, size.lines

        # split incoming text into individual lines and append to buffer
        for line in text.splitlines('\n'):
            line = line.strip()
            if line != '':
                self.buffer.append(line)

        # determine how many lines we can display (rows 2 through rows-1)
        while len(self.buffer) > (rows-3):
            self.buffer.pop(0)

        # clear rows 2..(rows-1)
        
        for r in range(2,rows-2):
            sys.__stdout__.write(f"\033[{r};1H\033[K")

        # write each line in standout (reverse) mode, padded/truncated to full width
        for idx, line in enumerate(self.buffer):
            #content = line[:cols].ljust(cols)
            content = line
            sys.__stdout__.write(f"\033[{idx+2};1H\t{ansi['fg_bright_magenta']}{content} Index:{idx} {len(self.buffer)} rows:{rows} \033[0m")

        # move cursor to bottom line for input
        sys.__stdout__.write(f"\033[{rows};1H")
        sys.__stdout__.flush()


class pyMenuItem:
    def __init__(self, name, hotkey=None, action=None, args=None, argprompt=None):
        self.name = name
        self.hotkey = hotkey if hotkey else None
        self.action = action if action else lambda: print(f"Action for {name} executed")
        self.args = args if args else ()
        self.argprompt = argprompt if argprompt else None
        self.index = -1
        self.parent = None

    def execute(self):
        if callable(self.action):
            self.action(*self.args)
        else:
            print(f"Executing action for {self.name} with args {self.args}")
 
class pyMenu:
    
    def __init__(self, name: str, action=None, hotkey=None):
        self.name = name
        self.hotkey = hotkey
        self.index = -1 # Index will be set when added to a menu
        self.items = OrderedDict()  # Use OrderedDict to maintain order of items 
        self.width = len(name)  # Width based on name length 
        self.location = [0,0] 
        self.current_item = -1
        self.parent = None
        self._visible = False

    @property
    def visible(self) -> bool:
        """The ‘name’ property getter."""
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        """The ‘name’ property setter—runs when you write p.name = ..."""
        if not isinstance(value, bool):
            raise TypeError("name must be a string")
        
        self._visible = value
        if self._visible:
            self.draw
        else:
            self.erase()

    @property
    def height(self):
        return len(self.items)
    
    def add_item(self, item: Union[pyMenuItem, 'pyMenu']):
        if isinstance(item, pyMenuItem) or isinstance(item,pyMenu):
            item.index = len(self.items)
            self.items[item.name] = item 
            self.width = max(self.width,len(item.name)+4)
            item.parent = self

    def paint_if_visible(self):
        if self.visible:
            self.draw()
        for item in self.items:
            if isinstance(self.items[item],pyMenu):
                self.items[item].paint_if_visible()
    
    def hide_menu_tree(self):
        self.visible = False
        self.current_item = -1
        if self.parent and not isinstance(self.parent,TTYMenu):
            self.parent.hide_menu_tree()
        if isinstance(self.parent,TTYMenu):
            self.parent.current_menu = self.parent

    def draw(self):
        Terminal.hide_cursor()
        y = self.location[0]+1
        for index, item in enumerate(self.items.values()):
            Terminal.move_to(y,self.location[1]-1)
            #sys.stdout.write(f"\033[{y};{self.location[1]-1}H")
            name = item.name + "   ►" if isinstance(item,pyMenu) else item.name
            if item.index == self.current_item:
                sys.stdout.write(
                    f"{ansi['reverse']}{ansi['fg_white']}{ansi['bg_blue']}| "
                    f"{name:<{self.width}}|"
                    f"{ansi['reset']}"
                )
            else:                
                sys.stdout.write(
                    f"{ansi['bg_bright_blue']}| "
                    f"{name:<{self.width}}|"
                    f"{ansi['reset']}"
                )
            y = y + 1
        Terminal.move_to(y,self.location[1]-1)
        #sys.stdout.write(f"\033[{y};{self.location[1]-1}H")
        sys.stdout.write(f"{ansi['bg_bright_blue']}\\{'_' * (self.width+1)}/")
        sys.stdout.write(f"{ansi['reset']}")
        Terminal.hide_cursor()
    
    def erase(self):
        """
        Clears the full menu area where draw() will paint.
        """
        row_start = self.location[0] + 1
        col_start = self.location[1] - 1
        # include the trailing '|' and bottom border
        col_end = col_start + self.width + 2  

        for y in range(row_start, row_start + self.height + 1):
            Terminal.clear_region(y, col_start, col_end)
        self.current_item = -1
        
    def execute(self):
        self.visible = True        

    @property
    def hight(self):
        """
        Returns the height of the menu based on the number of items.
        """
        return len(self.items)
    
class TTYMenu:
    """
    Base class for TTY menu definitions.
    """
    def __init__(self, name: str):
        self.name = name
        self.items = {}
        self.current_item = -1
        self.current_menu = self
        self.location = [1, 1]  # Default location
        self.instruction_location = (0, 0)
        
        self.debug_location = (0, 0)
        size = os.get_terminal_size()
        self.columns = size.columns
        self.rows = size.lines
        self.feedback_location = (self.rows-1, 0)
        self.last_feedback = ""

        self.stdout = pyMenuStdOut()
        sys.stdout.write(f"{ansi['clear_screen']}")  # Hide cursor
    
    def add_menu_item(self, item: pyMenu):
        """
        Adds a menu item to the menu.
        """
        if isinstance(item, pyMenu):
            item.index = len(self.items)
            item.parent = self
            self.items[item.name] = item          
        else:
            raise TypeError("Item must be an instance of pyMenu")
        
    def feedback(self, message: str):
        """
        Print a feedback message to the terminal at the configured feedback_location.
        Clears the line first to ensure no leftover text remains.

        Parameters:
        - message (str): The feedback message to display.
        """
        row, col = self.feedback_location

        # Move cursor to feedback location and clear the line
        sys.stdout.write(ansi["save_cursor"])  # Save cursor position 
        sys.stdout.write(f"\033[{row};{col}H")  # Move cursor
        sys.stdout.write(ansi['clear_line']  + ansi['bold'])    # Clear the line
        sys.stdout.write(message + ansi['reset'])               # Print the message
        #sys.stdout.write(ansi["restore_cursor"] + ansi["show_cursor"])
        sys.stdout.flush()
        self.last_feedback = message

    def draw(self):
        """
        Draws the menu on the terminal.
        """
        size = os.get_terminal_size()
        self.columns = size.columns
        self.rows = size.lines
        #sys.stdout.write(ansi['clear_screen']+ansi["cursor_home"] + ansi["hide_cursor"])
        y, x = self.location
        sys.stdout.write(ansi["save_cursor"])  # Save cursor position   
        sys.stdout.write(f"\033[{y};{x}H")  # Move cursor to row y, column x
                
        menu_text = ""
        for index, item in enumerate(self.items.values()):
            item.location = [y, x]
            
            if item.index == self.current_item:
                menu_text = f"{ansi['reverse']}{ansi['bold']}{ansi['fg_bright_blue']}  {item.name}  {ansi['reset']}|"
            else:
                menu_text = f"{ansi['fg_green']}  {item.name}  {ansi['reset']}|"
            x = x + len(f"  {item.name}  |")
            sys.stdout.write(f"{menu_text}")
        for index, item in enumerate(self.items.values()):
            item.paint_if_visible()
        self.feedback(self.last_feedback)


        #sys.stdout.write(ansi["restore_cursor"] + ansi["show_cursor"])
        #sys.stdout.flush()

    def get_user_input(self):
        """
        Reads keypresses and returns a list of raw bytes.
        Handles arrow keys (two‑byte sequences) and normal keys.
        """
        ch1 = msvcrt.getch()               # bytes
        if ch1 in (b'\x00', b'\xe0'):      # special‑key prefix
            ch2 = msvcrt.getch()           # actual arrow/function key code
            return [ch1, ch2]
        return [ch1]
        
    def show(self, location=None):
        """
        Displays the menu and waits for user input.
        """       
        while True:
            self.draw()
            result = self.get_user_input()
            self.feedback(f"{type(result)}:{result}")
            if self.current_menu == self:             
                if result:
                    if result == RIGHT_KEY or result == XRIGHT_KEY:
                        item = self.items.get(list(self.items.keys())[self.current_item])
                        item.visible = False
                        self.current_item = self.current_item + 1 if self.current_item + 1 < len(self.items) else 0
                        
                        item = self.items.get(list(self.items.keys())[self.current_item])
                        self.feedback(f"Current index: {self.current_item} {item.location}")
                    elif result == LEFT_KEY or result == XLEFT_KEY:
                        item = self.items.get(list(self.items.keys())[self.current_item])
                        item.visible = False
                        self.current_item = self.current_item - 1 if self.current_item - 1 >= 0 else len(self.items) - 1
                        item = self.items.get(list(self.items.keys())[self.current_item])
                        self.feedback(f"Current index: {self.current_item} {item.location}")
                    elif result == DOWN_KEY or result == XDOWN_KEY:
                        
                        item = self.items.get(list(self.items.keys())[self.current_item])
                        self.feedback(f"Down Key: {self.current_item} {item.location}")
                        if self.current_item >= 0:
                            item = self.items.get(list(self.items.keys())[self.current_item])
                            if len(item.items) > 0:
                                if not item.visible:
                                    item.visible = True
                                else:
                                    item.current_item = 0
                                    self.current_menu = item

                    elif result == ENTER_KEY:
                        self.feedback(f"Current index: {self.current_item}")
                        #self.handle_selection(self.current_index)
                    elif result[0] == b'\x1b':  # ESC key
                        
                        self.feedback("Exiting...")
                        return None
                    self.draw()  # Redraw the menu to reflect changes
            else:
                if result == UP_KEY or result == XUP_KEY:
                    self.feedback(f"Up key: {self.current_item} ")
                    if self.current_menu.current_item == 0:
                        self.current_menu.current_item = -1
                        if self.current_menu.parent == self:
                            self.feedback(f"Top level")
                            self.current_menu.visible = False
                            self.current_menu.erase()
                            self.current_menu = self
                        else:
                            self.current_menu.visible = False
                            self.current_menu.erase()
                            self.current_menu = self.current_menu.parent
                    elif self.current_menu.current_item == -1:
                        self.current_menu.visible = False
                        self.current_menu = self.current_menu.parent
                        if self.current_menu.current_item > 0:
                            self.current_menu.current_item = self.current_menu.current_item - 1

                            
                    else:
                        self.current_menu.current_item = self.current_menu.current_item - 1

                elif result == DOWN_KEY or result == XDOWN_KEY:
                    if self.current_menu.current_item < len(self.current_menu.items)-1:
                        self.current_menu.current_item = self.current_menu.current_item + 1
                elif result == RIGHT_KEY or result == XRIGHT_KEY:
                    
                    item = self.current_menu.items.get(list(self.current_menu.items.keys())[self.current_menu.current_item])
                    if isinstance(item,pyMenu) and len(item.items) > 0:
                        
                        item.location = [self.current_menu.location[0]+self.current_menu.current_item,self.current_menu.location[1]+self.current_menu.width-2]
                        self.current_menu = item
                        
                        item.visible = True
                        #item.draw()
                        self.feedback(f"Submenu: {item.name}")
                    self.feedback(f"Current Menu: {self.current_menu.name} Current Item: {self.current_menu.current_item} {type(item)}")
                elif result == ENTER_KEY:
                    
                    if self.current_menu.current_item >=0 and self.current_menu.current_item <= len(self.current_menu.items)-1:
                        item = self.current_menu.items.get(list(self.current_menu.items.keys())[self.current_menu.current_item])
                        if item:
                            if isinstance(item,pyMenu) and len(item.items) > 0:
                                if item.visible:
                                    item.current_item = 0
                                    self.current_menu = item
                                else:
                                    item.location = [self.current_menu.location[0]+self.current_menu.current_item,self.current_menu.location[1]+self.current_menu.width-2]
                                    item.visible = True
                                    self.current_menu = item
                            elif isinstance(item, pyMenuItem):
                                self.feedback(f"Executing Current Item: {item.name}")
                                self.current_menu.hide_menu_tree()
                                sys.stdout = self.stdout
                                item.execute()
                                sys.stdout = sys.__stdout__
                                
                            else:
                                pass

                elif result[0] == b'\x1b':  # ESC key
                    self.current_menu.current_item = -1
                    if self.current_menu.parent == self:
                        self.feedback(f"Top level")
                        self.current_menu.visible = False
                        self.current_menu = self




    
menus = TTYMenu("Main Menu")
file_menu = pyMenu("File", action=lambda: print("File action executed"), hotkey='F')
edit_menu = pyMenu("Edit", action=lambda: print("Edit action executed"), hotkey='E')
view_menu = pyMenu("View", action=lambda: print("View action executed"), hotkey='V')
help_menu = pyMenu("Help", action=lambda: print("Help action executed"), hotkey='H')
open_search_menu = pyMenu("OpenSearch", action=lambda: print("File action executed"), hotkey='F')
menus.add_menu_item(file_menu)
menus.add_menu_item(edit_menu)      
menus.add_menu_item(view_menu)
menus.add_menu_item(help_menu)
menus.add_menu_item(open_search_menu)

def quit():
    sys.stdout = pyMenuStdOut()
    print("testing,1 2 3")
    exit()

def test_print():

    for n in range(50):
        print(n)

    return

file_menu.add_item(pyMenuItem("Exit", action=quit, hotkey='X'))
edit_menu.add_item(pyMenuItem("Test Print to StdOut", action=test_print, hotkey='X'))
edit_menu.add_item(pyMenuItem("Item_____2", action=lambda: print("Edit action executed"), hotkey='X'))
mi3 = pyMenu("MenuItem________3", hotkey='X')
mi4 = pyMenu("SubLevel________3", hotkey='X')
edit_menu.add_item(mi3)
mi3.add_item(pyMenuItem("Item_____1", action=lambda: print("Edit action executed"), hotkey='X'))
mi3.add_item(pyMenuItem("Item_____2", action=lambda: print("Edit action executed"), hotkey='X'))
mi3.add_item(mi4)


menus.draw()
text = ""
for index, item in enumerate(menus.items.values()):
    text += f"{item.name}:{item.location} "
menus.feedback(text)
menus.show()
