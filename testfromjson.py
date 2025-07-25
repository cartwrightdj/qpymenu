from qpymenu import pyMenu, pyMenuItem

with open('testfrom.json', 'r') as file:
    import json
    data = json.load(file)
menu = pyMenu.from_json(data)

menu.execute()