# ============================================================
# pymenu.py v.5.1
# 
# A simple terminal menu system with ANSI formatting.
# Features:
#   - Nested menus and menu items
#   - ANSI color and formatting support
#   - Logs actions and displays them on the right side
#   - Supports threaded execution of menu item actions
#   - Prompts for arguments if "" is passed as args
#
# Usage:
#   Define menu items and submenus, then call menu.execute()
#
# Author: David J. Cartwright davidcartwright@hotmail.com
# Date: 2025-07-23
#
# update to wait for key press after execution errors
# ============================================================

import shutil
import threading
import ast
import importlib

from .ansi import ansi

# ============================================================
# pyMenu class
#
# A class representing a terminal menu system with ANSI formatting.
#
# Features:
#   - Supports nested menus and menu items
#   - ANSI color and formatting for menu display
#   - Keeps a log of actions and displays them on the right side
#   - Allows threaded execution of menu item actions
#   - Prompts for arguments if "" is passed as args to a menu item
#
# Usage:
#   Create a pyMenu instance, add pyMenuItem or pyMenu (as submenus),
#   then call menu.execute() to start the menu loop.
#
# Methods:
#   - log_action(message): Add a message to the log
#   - draw(): Render the menu and log to the terminal
#   - execute(): Main menu loop for user interaction
#   - setformat(title_format, item_format): Set ANSI formatting for title/items
#   - additem(item): Add a pyMenuItem to the menu
#   - addsubmenu(submenu): Add a pyMenu as a submenu
#
# Date: 2025-07-23
# ============================================================
class pyMenu():
    """
    A terminal-based menu system that supports nested menus, ANSI formatting, logging, and threaded execution of actions.

    Features:
        - Nested submenus
        - ANSI color formatting
        - Logging pane
        - Threaded item execution
        - Optional argument prompting

    Example:
        >>> main = pyMenu("Main Menu")
        >>> item = pyMenuItem("Greet", action=lambda: print("Hello!"))
        >>> main.additem(item)
        >>> main.execute()

    Attributes:
        name (str): The name shown at the top of the menu.
        items (list): Menu items.
        current_index (int): Current selection index for navigation.
    """
    def __init__(self, name: str = 'Main Menu'):
        self.name = name
        self.items = []
        self.title_format = ansi["fg_bright_blue"] + ansi["bold"]
        self.item_format = ansi["fg_bright_green"]
        self.parent = None
        self.log = []

    def _log_action(self, message):
        self.log.append(message)
        if len(self.log) > 20:  # Keep last 20 logs
            self.log.pop(0)

    def _draw(self):
        columns, rows = shutil.get_terminal_size(fallback=(80, 24))
        menu_width = columns // 2
        print(ansi['clear_screen'] + ansi['cursor_home'], end='')
        # Draw menu on left
        print(f"{self.title_format}{self.name}{ansi['reset']}")
        print("=" * len(self.name))
        for index, item in enumerate(self.items, start=1):
            print(f"{index}. {item.name} ({'>>' if isinstance(item, pyMenu) else 'Action'})")
        if self.parent:
            print(f"{ansi['fg_bright_yellow']}0. Parent Menu: {self.parent.name}{ansi['reset']}")
        else:
            print(f"{ansi['fg_bright_yellow']}0. Exit{ansi['reset']}")
        # Draw log on right
        print(ansi['save_cursor'], end='')
        for i, log_entry in enumerate(self.log[-rows:]):
            print(f"\033[{i+1};{menu_width+2}H{ansi['fg_bright_cyan']}{log_entry}{ansi['reset']}")
        print(ansi['restore_cursor'], end='')

    def execute(self):
        """
        Starts the interactive menu loop.

        This method continuously displays the current menu, waits for user input,
        and navigates or executes based on the selection. Input of 0 returns to the
        parent menu or exits if at the root level. Valid numbered choices execute
        items or enter submenus.

        Logs each action and handles invalid input gracefully.
        """
        current_menu = self
        while True:
            current_menu._draw()
            try:
                choice = int(input("Select an option: "))
                if choice == 0:
                    if current_menu.parent:
                        current_menu = current_menu.parent
                    else:
                        self._log_action("Exited menu.")
                        break
                elif 1 <= choice <= len(current_menu.items):
                    selected = current_menu.items[choice - 1]
                    if isinstance(selected, pyMenu):
                        current_menu = selected
                    else:
                        selected.execute()
                        self._log_action(f"Executed: {selected.name}")
                else:
                    self._log_action("Invalid selection.")
            except ValueError:
                self._log_action("Invalid input.")
    
    def setformat(self, title_format: str = ansi["fg_bright_blue"] + ansi["bold"],
                     item_format: str = ansi["fg_bright_green"]):
        """
        Sets the ANSI color format for displaying the menu title and items.

        Args:
            title_format (str): ANSI escape string for formatting the menu title.
            item_format (str): ANSI escape string for formatting the menu items.
        """
        self.title_format = title_format
        self.item_format = item_format
    
    def additem(self, item: 'pyMenuItem'):
        """
        Adds a pyMenuItem to the current menu.

        Args:
            item (pyMenuItem): The menu item to be added.

        Raises:
            TypeError: If the provided item is not an instance of pyMenuItem.
        """
        if isinstance(item, pyMenuItem):
            self.items.append(item)
        else:
            raise TypeError("Item must be an instance of pyMenuItem.")
        
    def addsubmenu(self, submenu: 'pyMenu'):
        """
        Adds a submenu (pyMenu) to the current menu.

        The submenu becomes a child of this menu, enabling nested navigation.

        Args:
            submenu (pyMenu): The submenu instance to add.
        """
        if isinstance(submenu, pyMenu):
            submenu.parent = self
            self.items.append(submenu)
        else:
            raise TypeError("Submenu must be an instance of pyMenu.")

    @staticmethod
    def from_json(data: dict) -> 'pyMenu':
        """
        Creates a pyMenu instance (including nested submenus) from a JSON-like dictionary.

        Args:
            data (dict): A dictionary representing the menu structure.
                        Expected keys: 'name', 'items', where each item has 'type' ('item' or 'submenu').

        Returns:
            pyMenu: A fully constructed pyMenu object with items and nested submenus.

        Raises:
            ValueError: If the input structure is invalid.
        """
        if not isinstance(data, dict):
            raise ValueError("Expected top-level JSON to be a dictionary.")

        menu = pyMenu(name=data.get("name", "Menu"))

        for index, entry in enumerate(data.get("items", []), start=1):
            if not isinstance(entry, dict):
                print(f"[ERROR] Item {index} is not a dictionary: {entry!r}")
                continue

            entry_type = entry.get("type")
            try:
                if entry_type == "item":
                    item = pyMenuItem._from_dict(entry)
                    menu.additem(item)
                elif entry_type == "submenu":
                    submenu = pyMenu.from_json(entry)
                    menu.addsubmenu(submenu)
                else:
                    print(f"[WARNING] Skipped unknown item type '{entry_type}' at index {index}: {entry.get('name', '?')}")
            except Exception as e:
                print(f"[ERROR] Failed to load item at index {index} with name '{entry.get('name', '?')}'.")
                print(f"        Reason: {type(e).__name__}: {e}")
                print(f"        Entry: {entry!r}")
                continue  # Continue loading other items even if one fails

        return menu

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

    def __init__(self, name: str, action: callable = None, wait=True, args=None, threaded=False):
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
        self.action = action
        self.wait = wait
        self.args = args  # Default args or None
        self.threaded = threaded  # If True, run action in a separate thread

    def _execute(self):
        if callable(self.action):
            args = self.args
            # Only prompt for arguments if args is exactly an empty string
            if args == "":
                arg_input = input(f"Enter arguments for {self.name} (comma-separated, or leave blank for none): ")
                if arg_input.strip():
                    try:
                        args = ast.literal_eval(f"({arg_input.strip()},)")
                    except Exception as e:
                        print(f"Error parsing arguments: {e}")
                        print(ansi['bg_cyan'] + 'Press any key to return to menu' + ansi['reset'], end='')          
                        input()
                        args = ()
                else:
                    args = ()
            elif args is None:
                args = ()
            # If args is a single value, make it a tuple
            if not isinstance(args, tuple):
                args = (args,)
            if self.threaded:
                t = threading.Thread(target=self.action, args=args)
                t.start()
                if self.wait:
                    t.join()
            else:
                self.action(*args)
            if self.wait and not self.threaded:
                print(ansi['bg_cyan'] + 'Press any key to return to menu' + ansi['reset'], end='')          
                input()
        else:
            print(f"Action for {self.name} is not callable.")
            print(ansi['bg_cyan'] + 'Press any key to return to menu' + ansi['reset'], end='')          
            input()

    @staticmethod
    def _from_dict(data: dict) -> 'pyMenuItem':
        name = data["name"]
        action_path = data.get("action")
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

def test_function(test_arg: str = "Hello from test_function!"):
    print(test_arg) 
