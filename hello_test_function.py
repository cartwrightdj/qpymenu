from qpymenu import pyMenu, pyMenuItem

def test_function():
    print("Hello from test_function!")

menu = pyMenu("Example Menu")
# Add a test item to the menu that calls  <test_function()> with no arguments
menu.additem(pyMenuItem("Test Item", test_function))

if __name__ == "__main__":
    menu.execute()