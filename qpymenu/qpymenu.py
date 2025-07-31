# ============================================================
# pymenu.py v.5.1
# 
# A simple terminal menu system with ANSI formatting.
# Features:
#   - Nested menus and menu items
#   - ANSI color and formatting support
#   - Status Bar at bottom of terminal
#   - Supports threaded execution of menu item actions
#   - Arguments fro Menu Item actions can be provided, or prompted for
#
# Usage:
#   Define menu items and submenus, then call menu.activate()
#
# Author: David J. Cartwright davidcartwright@hotmail.com
# Date: 2025-07-23
#
# update to wait for key press after execution errors
# ============================================================

import sys
import ast
import threading
import inspect

from enum import Enum
from collections import OrderedDict
from .ansi import ansi
from .terminal import Terminal, read_key
from typing import Union, Callable
import os
import importlib

# ============================================================
# pyMenuItem class
#
# Represents a single menu item in the terminal menu system.
#
# Features:
#   - Stores a name, an action (callable), and optional arguments
#   - Can execute its action, optionally in a separate thread
#   - Prompts for arguments if args is set to an empty string ("")
#   - Waits for user input after execution if wait=True
#
# Args:
#   name (str): The display name of the menu item
#   action (callable): The function to execute when selected
#   hotkey (str): Used for Ctrl - X execution of items
#   wait (bool): Whether to wait for key press after execution
#   args: Arguments to pass to the action (None, "", or tuple)
#   threaded (bool): If True, run the action in a separate thread
#
# Methods:
#   - execute(): Runs the action with provided arguments and handles user prompts
# ============================================================

class pyMenuItem():
    """
    Represents a single menu item that can execute a callable action.

    Supports:
        - Optional arguments
        - Threaded execution
        - Argument prompting at runtime
        - Optional wait for keypress after execution

    Attributes:
        - name (str): Display name of the item in the menu.
        - action (callable, optional): The function to execute when selected.
        - wait (bool): If True, waits for keypress after execution.
        - args (any): Arguments to pass to the action (None, tuple, or special "" to prompt).
        - threaded (bool): If True, runs the action in a new thread.
    """

    def __init__(self, name: str, hotkey: str | None = None, action: callable = None, wait=True, args=None, threaded=False):
        """
        Initializes a new pyMenuItem.

        Args:
            name (str): Display name of the item in the menu.
            action (callable, optional): The function to execute when selected.
            wait (bool): If True, waits for keypress after execution.
            args (any): Arguments to pass to the action (None, tuple, or special "" to prompt).
            threaded (bool): If True, runs the action in a new thread.
        """
        self.name = name
        self.hotkey = hotkey[:1] if hotkey else None
        self.action = action
        self.wait = wait
        self.args = args  # Default args or None
        self.threaded = threaded  # If True, run action in a separate thread
        self._index = -1
        self._parent = None    

    def execute(self):
        Terminal.show_cursor()
        if callable(self.action):
            args = self.args
            # Only prompt for arguments if args is exactly an empty string
            if args == "":
                prompt = self._prompt_for_arguments(self.action)
                self.status(prompt)
                arg_input = Terminal.read_line()
                if arg_input.strip():
                    try:
                        args = ast.literal_eval(f"({arg_input.strip()},)")
                    except Exception as e:
                        sys.stdout.write(f"{ansi['bg_red']}Error parsing arguments: {e}\n"
                                        "ansi['bg_cyan'] + 'Press any key to return to menu' + ansi['reset']")          
                        read_key()
                        args = ()
                        return False
                else:
                    args = ()
            elif args is None:
                args = ()
            # If args is a single value, make it a tuple
            if not isinstance(args, tuple):
                args = (args,)
            # 0.6.3 - changed to deal with both cases, Added error handling for action execution
            try:
                if self.threaded:
                    t = threading.Thread(target=self.action, args=args)
                    t.start()
                    if self.wait:
                        t.join()
                else:  
                    sys.stdout = Terminal.pyMenuStdOut()                
                    self.action(*args)
                    sys.stdout = sys.__stdout__
            except Exception as e:
                sys.stdout.write(f"{ansi['bg_red']} Error executing action for '{self.name}': {e} {ansi['reset']}\n"
                                        f"{ansi['bg_cyan']}'Press any key to return to menu'{ansi['reset']}")          
                read_key()
                Terminal.clear_screen()
                return False
                
            if self.wait and not self.threaded:
                sys.stdout.write(ansi['bg_cyan'] + 'Press any key to return to menu' + ansi['reset'])          
                read_key()
                Terminal.clear_screen()
                return False

               
        else:
            sys.stdout.write("Action for {self.name} is not callable.")
            #self.feedback(ansi['bg_cyan'] + 'Press any key to return to menu' + ansi['reset'])   
            sys.stdout.write("About to call input")       
            read_key()
            sys.stdout.write("Called input")
        
        return False

    def status(self, message: str):
        """
        Print a feedback message to the terminal at the configured feedback_location.
        Clears the line first to ensure no leftover text remains.

        Parameters:
        - message (str): The feedback message to display.
        """
        size = os.get_terminal_size()
        col = size.columns
        row = size.lines
        

        # Move cursor to feedback location and clear the line
        sys.stdout.write(ansi["save_cursor"])  # Save cursor position 
        Terminal.move_to(row,1)
        #sys.stdout.write(f"\033[{row};{col}H")  # Move cursor
        sys.stdout.write(ansi['clear_line']  + ansi['bold'])    # Clear the line
        sys.stdout.write(message + ansi['reset'])               # Print the message
        #sys.stdout.write(ansi["restore_cursor"] + ansi["show_cursor"])
        
        self.last_feedback = message

    def _prompt_for_arguments(self, func: Callable) -> str:
        """
        Displays the argument names and type annotations for the given function.
        
        Args:
            func (Callable): The function to inspect.
        """
        sig = inspect.signature(func)
        prompt = f"Enter arguments for {func.__name__} " + \
             " ".join(f"[{n}: {p.annotation or 'Any'}]" for n,p in sig.parameters.items()) + " "
        return prompt

    @staticmethod
    def _from_dict(data: dict) -> 'pyMenuItem':
        name = data["name"]
        action_path: str = data.get("action","")
        module_path, func_name = action_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        action = getattr(module, func_name) if action_path else None

        return pyMenuItem(
            name=name,
            action=action,
            args=data.get("args", None),
            wait=data.get("wait", True),
            threaded=data.get("threaded", False)
        )
    
    
    
    
        """
        Print a feedback message to the terminal at the configured feedback_location.
        Clears the line first to ensure no leftover text remains.

        Parameters:
        - message (str): The feedback message to display.
        """
        size = os.get_terminal_size()
        col = size.columns
        row = size.lines
        

        # Move cursor to feedback location and clear the line
        sys.stdout.write(ansi["save_cursor"])  # Save cursor position 
        Terminal.move_to(row,1)
        #sys.stdout.write(f"\033[{row};{col}H")  # Move cursor
        sys.stdout.write(ansi['clear_line']  + ansi['bold'])    # Clear the line
        sys.stdout.write(message + ansi['reset'])               # Print the message
        #sys.stdout.write(ansi["restore_cursor"] + ansi["show_cursor"])
        sys.stdout.flush()
        self.last_feedback = message

class pyMenu():
    def __init__(self, name: str, action=None, hotkey=None,type:str = 'V'):
        self.name = name
        self.hotkey = hotkey
        self._index = -1 # Index will be set when added to a menu
        self._items = OrderedDict()  # Use OrderedDict to maintain order of items 
        self._width = len(name)  # Width based on name length 
        self._location = [1,1] 
        self._current_index = -1
        self._parent = None
        #self._visible = False
        self._type = type
        self._current_menu = self
        self._active = True
    
    def add_item(self, item: 'Union(pyMenu,pyMenuItem)'):
        # TODO check for overwrite
        if isinstance(item,pyMenu) or isinstance(item,pyMenuItem):
            item._index = len(self._items)
            self._items[item.name] = item 
            self._width = max(self._width,len(item.name)+4)
            item._parent = self

    @staticmethod
    def version() -> str:
        """
        Returns the version of the pyMenuItem class.
        
        This is useful for checking compatibility or debugging.
        """
        return "0.8.0"
        
    @property
    def _is_valid(self):
        return len(self._items) > 0
    
    @property
    def y(self):
        return self._location[0]

    @property
    def x(self):
        return self._location[1]
    
    @property
    def height(self):
        if self._type == 'H':
            return 1
        return len(self._items)
    
    
    def _draw(self):      
        if self._type == 'H':
            Terminal.move_to(self.y,self.x)
            y, x = self._location
            menu_text = ""
            for index, item in enumerate(self._items.values()):
                item._location = [y+1, x]
                ctrlkey = f'     Ctrl + {self.hotkey}' if self.hotkey else ''
                if item._index == self._current_index:
                    menu_text = f"{ansi['reverse']}{ansi['bold']}{ansi['fg_bright_blue']}  {item.name} {ctrlkey}  {ansi['reset']}|"
                else:
                    menu_text = f"{ansi['fg_green']}  {item.name} {ctrlkey}  {ansi['reset']}|"
                x = x + len(f"  {item.name}  |")
                sys.stdout.write(f"{menu_text}")
        elif self._type == 'V':
            y = self._current_menu.y
            for index, item in enumerate(self._current_menu._items.values()):
                Terminal.move_to(y,self._current_menu._location[1]-1)
                name = item.name 
                if isinstance(item,pyMenu):
                    name += "   ►"
                    item._location = [y,self._current_menu.x + self._current_menu._width]

                if item._index == self._current_menu._current_index:
                    sys.stdout.write(
                        f"{ansi['reverse']}{ansi['fg_white']}{ansi['bg_blue']}| "
                        f"{name:<{self._current_menu._width}}|"
                        f"{ansi['reset']}"
                    )
                else:                
                    sys.stdout.write(
                        f"{ansi['bg_bright_blue']}| "
                        f"{name:<{self._current_menu._width}}|"
                        f"{ansi['reset']}"
                    )
                y = y + 1
            
    def _erase(self):

        
        """
        Clears the full menu area where draw() will paint.
        """
        row_start = self._location[0] 
        col_start = self._location[1] -1
        # include the trailing '|' and bottom border
        col_end = col_start + self._width + 2  

        for y in range(row_start, row_start + self.height + 1):
            Terminal.clear_region(y, col_start, col_end)
        self._current_index = -1

    def colapse_menu_tree(self):
        if self._parent is not None:
            self._erase()
            self._parent.colapse_menu_tree()
        #self._current_menu = self
        #self._current_index = 0

    def _get_user_input(self):
        """
        Reads keypresses and returns a list of raw bytes.
        Handles arrow keys (two‑byte sequences) and normal keys.
        """
        return read_key()

    def _get_current_item(self):
        item: pyMenu = self._current_menu._items.get(list(self._current_menu._items.keys())[self._current_menu._current_index],None)  # type: ignore
        if self._current_index == -1:
            return None
        return item
    
    def _dec_current_index(self) -> bool:
        """
        Decriments the 'current_index' property. If index drops below 0, dispose of menu

        Returns pyMenu
        """
        
        current_index = self._current_index
        if current_index <= 0 and self._type == 'V':
            return False
        if current_index <= 0 and self._type == 'H':
            self._current_index = 0
            return True
        else:
            self._current_index = current_index - 1
        return True
    
    def _inc_current_index(self) -> None: # type: ignore
        """
        Decriments the 'current_index' property. If index drops below 0, dispose of menu

        Returns current or parent menu
        """
        current_index = self._current_index
        if current_index < len(self._items)-1:
            self._current_index = current_index + 1

    def _on_up(self):
        if self._current_menu._type == 'H':
            pass
        else:
            if not self._current_menu._dec_current_index():
                self._current_menu._erase()
                self._current_menu = self._current_menu._parent
            else:
                self._current_menu._draw()
        
        return True
    
    def _on_down(self):
        if self._current_menu._type == 'H':
            item = self._get_current_item()
            if item and item._is_valid:
                self._current_menu = item
                item._draw()
        else:
            self.status(f'Current Menu: {self._current_menu.name}')
            self._current_menu._inc_current_index()
            self._current_menu._draw()

        
        
        return True

    def _on_left(self):
        if self._current_menu._type == 'H':
            self._current_menu._dec_current_index()
        elif self._current_menu._type == 'V':
            if self._current_menu._current_index == 0 or self._current_menu._current_index == -1:
                self._current_menu._current_index = -1
                self._current_menu._erase()
                self._current_menu = self._current_menu._parent
        return True

    def _on_right(self):
        if self._current_menu._type == 'H':
            self._current_menu._inc_current_index()
        else:
             
            item = self._get_current_item()
            
            if self._current_menu._current_index == -1:
                self._current_menu._current_index = 0
            elif isinstance(item,pyMenu) and item._is_valid:
                item._draw()
                self._current_menu = item 
        return True

    def _on_enter(self):
        if self._current_menu._type == 'H':
            item = self._get_current_item()
            if item and item._is_valid:
                self._current_menu = item
                item._draw()
        else:
             
            item = self._get_current_item()
            
            if self._current_menu._current_index == -1:
                self._current_menu._current_index = 0
            elif isinstance(item,pyMenu) and item._is_valid:
                item._draw()
                self._current_menu = item 
            elif isinstance(item,pyMenuItem):
                self._current_menu.colapse_menu_tree()
                item.execute()
                self._current_menu = self
                self._draw()
        return True
              
    def show(self):
        if self._is_valid:
            if self._parent is None: Terminal.clear_screen()
            while True:
                self._current_menu._draw()
                self.status(f'Menu: {self._current_menu.name}, Index: {self._current_menu._current_index}, Type: {self._current_menu._type} y:{self._current_menu.y} x:{self._current_menu.x}')
                result = self._get_user_input()
                
                if result == "UP":
                    self._on_up()
                             
                elif result == "RIGHT":
                    self._on_right()
                           
                elif result == "LEFT":
                    self._on_left()
                                
                elif result == "DOWN":
                    self._on_down()
                         
                elif result == 'ENTER':
                    self._on_enter()
                                             
    def status(self, message: str):
        """
        Print a feedback message to the terminal at the configured feedback_location.
        Clears the line first to ensure no leftover text remains.

        Parameters:
        - message (str): The feedback message to display.
        """
        size = os.get_terminal_size()
        col = size.columns
        row = size.lines
        

        # Move cursor to feedback location and clear the line
        sys.stdout.write(ansi["save_cursor"])  # Save cursor position 
        Terminal.move_to(row,1)
        #sys.stdout.write(f"\033[{row};{col}H")  # Move cursor
        sys.stdout.write(ansi['clear_line']  + ansi['bold'])    # Clear the line
        sys.stdout.write(message + ansi['reset'])               # Print the message
        #sys.stdout.write(ansi["restore_cursor"] + ansi["show_cursor"])
        
        self.last_feedback = message

    class Types():
        HorizontalBar = 'H'
        DropDown = 'V'



            

