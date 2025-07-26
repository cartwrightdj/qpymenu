# qPyMenu

A simple terminal menu system with ANSI formatting, logging, and threaded actions.


## Reference Documentation
[https://qpymenu.readthedocs.io/]

[https://pypi.org/project/qpymenu/0.6.0/]

```
pip install qpymenu
```

## Features

- Define Menus in JSON (new)
- Nested menus and menu items
- ANSI color and formatting support
- Logs actions and displays them on the right side
- Supports threaded execution of menu item actions
- Prompts for arguments if `""` is passed as args

## Usage

```python
from qpymenu import pyMenu, pyMenuItem

def test_function():
    print("Hello from test_function!")

menu = pyMenu("Example Menu")
menu.additem(pyMenuItem("Test Item", test_function))
menu.execute()
```



## 📘 Module: `qpymenu.qpymenu`

### Class: `pyMenu`

```python
pyMenu(name: str = "Main Menu")
```

A terminal-based menu system that supports nested menus, ANSI formatting, logging, and threaded execution of actions.

#### Attributes

- **name** (`str`): The name shown at the top of the menu.  
- **items** (`list`): Menu items.  
- **current_index** (`int`): Current selection index for navigation.  

#### Methods

##### `additem(item: pyMenuItem)`

Adds a `pyMenuItem` to the current menu.

- **Parameters**:  
  - `item` (`pyMenuItem`) – The menu item to be added.  
- **Raises**:  
  - `TypeError` – If the provided item is not an instance of `pyMenuItem`.

---

##### `addsubmenu(submenu: pyMenu)`

Adds a submenu (`pyMenu`) to the current menu.  
The submenu becomes a child of this menu, enabling nested navigation.

- **Parameters**:  
  - `submenu` (`pyMenu`) – The submenu instance to add.

---

##### `execute()`

Starts the interactive menu loop.  
This method continuously displays the current menu, waits for user input, and navigates or executes based on the selection.  
Input of `0` returns to the parent menu or exits if at the root level.  
Logs each action and handles invalid input gracefully.

---
## Defining Menus using JSON
example menus.json file
```json
{
  "name": "Main Menu",
  "items": [
    {
      "type": "item",
      "name": "Say Hello",
      "action": "qpymenu.test_function",
      "args": "",
      "wait": true,
      "threaded": false
    },
    {
      "type": "submenu",
      "name": "Utilities",
      "items": [
        {
          "type": "item",
          "name": "Show Time",
          "action": "qpymenu.test_function"
        }
      ]
    }
  ]
}
```
##### `@staticmethod from_json(data: dict) -> pyMenu`

Creates a `pyMenu` instance (including nested submenus) from a JSON-like dictionary.

- **Parameters**:  
  - `data` (`dict`) – A dictionary representing the menu structure.  
    Expected keys: `name`, `items`, where each item has `type` (`item` or `submenu`).  
- **Returns**:  
  - A fully constructed `pyMenu` object with items and nested submenus.  
- **Raises**:  
  - `ValueError` – If the input structure is invalid.

---

##### `setformat(title_format: str = '\x1b[94m\x1b[1m', item_format: str = '\x1b[92m')`

Sets the ANSI color format for displaying the menu title and items.

- **Parameters**:  
  - `title_format` (`str`) – ANSI escape string for formatting the menu title.  
  - `item_format` (`str`) – ANSI escape string for formatting the menu items.

---

### Class: `pyMenuItem`

```python
pyMenuItem(name: str, action: callable = None, wait=True, args=None, threaded=False)
```

Represents a single menu item that can execute a callable action.

#### Attributes

- **name** (`str`): Display name of the item in the menu.  
- **action** (`callable`, optional): The function to execute when selected.  
- **wait** (`bool`): If `True`, waits for keypress after execution.  
- **args** (`any`): Arguments to pass to the action (`None`, `tuple`, or `""` to prompt).  
- **threaded** (`bool`): If `True`, runs the action in a new thread.  

---



