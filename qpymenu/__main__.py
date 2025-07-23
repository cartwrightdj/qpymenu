from .qpymenu import pyMenu, pyMenuItem

def test_function():
    print("Hello from test_function!")

def add(a, b):
    print(f"The sum of {a} and {b} is {a + b}")

if __name__ == "__main__":
    menu = pyMenu("Example Menu")
    submenu = pyMenu("Sub Menu")
    menu.additem(pyMenuItem("Test Item", test_function))
    submenu.additem(pyMenuItem("Sub Item 1", test_function))
    submenu.additem(pyMenuItem("Sub Item 2", add, args=(5, 10)))
    menu.addsubmenu(submenu)
    menu.execute()