import msvcrt

UP = ('\x00', 'H')
DOWN = ('\x00', 'P')

print("Press ↑/↓ (ESC to quit)")
while True:
    ch1 = msvcrt.getwch()
    print(type(ch1),ch1)
    if ch1 in UP:
        print("UP arrow detected")
    elif ch1 in DOWN:
        print("DOWN arrow detected")
    elif ch1 == '\x1b':  # ESC
        break
