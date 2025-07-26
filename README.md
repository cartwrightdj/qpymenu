# pymenu

A simple terminal menu system with ANSI formatting, logging, and threaded actions.

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

## Defining Menus using JSON
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