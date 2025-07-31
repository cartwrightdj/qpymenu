import os
import sys

from typing import Tuple
from .ansi import ansi
import msvcrt

import ctypes


class Terminal:
    @staticmethod
    def move_to(row: int, col: int):
        # Clamp to 1-based positions
        row = max(1, row)
        col = max(1, col)
        sys.stdout.write(f"\033[{row};{col}H")
        sys.stdout.flush()

    @staticmethod
    def clear_screen():
        sys.stdout.write("\033[2J\033[H")   # clear + home
        sys.stdout.flush()
        

    @staticmethod
    def clear_line():
        sys.stdout.write("\033[2K")
        sys.stdout.flush()

    @staticmethod
    def hide_cursor():
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

    @staticmethod
    def show_cursor():
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    @staticmethod
    def save_cursor():
        sys.stdout.write("\033[s")
        sys.stdout.flush()

    @staticmethod
    def restore_cursor():
        sys.stdout.write("\033[u")
        sys.stdout.flush()

    @staticmethod
    def flush():
        sys.stdout.flush()
    
    @staticmethod
    def size() -> Tuple[int,int]:
        size = os.get_terminal_size()
        return size.columns, size.lines
        
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
    
    @staticmethod
    def set_cursor_color(color: str):
        """
        Set the text cursor color. `color` can be:
        - a named color, e.g. "red" or "green"
        - a hex RGB, e.g. "#ff0000"
        - an “rgb:” specifier, e.g. "rgb:ff/00/00"
        """
        # OSC 12 ; <color> BEL
        sys.stdout.write(f"\033]12;{color}\007")
        sys.stdout.flush()
    
    @staticmethod
    def reset_format():
        sys.stdout.write(ansi['reset'])
    
    @staticmethod
    def read_line() -> str:
        """
        Prompt the user with `prompt`, then read a full line via single-key reads.
        Echoes characters, handles Backspace, and returns the entered string.
        """
        # 1) Make sure cursor is visible
        Terminal.show_cursor()

        buf = []
        while True:
            ch = msvcrt.getwch()   # returns a Unicode char

            # ENTER finishes the line
            if ch in ('\r', '\n'):
                sys.stdout.write('\n')
                break

            # Backspace: remove last char if any
            if ch == '\x08':
                if buf:
                    buf.pop()
                    # move cursor back, overwrite, move back again
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
                continue

            # Normal character: echo & store
            buf.append(ch)
            sys.stdout.write(ch)
            sys.stdout.flush()

        

        return ''.join(buf)

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
            while len(self.buffer) > (rows-2):
                self.buffer.pop(0)

            self._write_buffer()

        def flush(self):
            sys.__stdout__.flush() # type: ignore

        def _write_buffer(self):
            for idx, line in enumerate(self.buffer):
                #content = line[:cols].ljust(cols)
                content = line
            
                sys.__stdout__.write(f"\033[{idx+2};1H")
                sys.__stdout__.write("\033[2K")
                sys.__stdout__.flush()
                sys.__stdout__.write(f"{ansi["fg_bright_white"]}> {content}\033[0m") # type: ignore

SCAN_CODES = {
    b'H': 'UP',
    b'P': 'DOWN',
    b'K': 'LEFT',
    b'M': 'RIGHT',
}

def read_key():
    first = msvcrt.getch()
    # if it’s a special key prefix (0x00 or 0xE0), grab the real code
    if first in (b'\x00', b'\xe0'):
        second = msvcrt.getch()
        return SCAN_CODES.get(second)  
    # else it’s a normal one‐byte key
    if first == b'\r':
        return 'ENTER'
    if first == b'\x1b':
        return 'ESC'
    try:
        return first.decode('utf-8')
    except UnicodeDecodeError:
        return None

def press_any_key(prompt: str = "Press any key to continue"):
    
    sys.stdout.write(prompt)
    Terminal.flush()
    read_key()
    return

class StdoutRedirect:
    def __init__(self, writer): self.writer, self.old = writer, sys.stdout
    def __enter__(self): sys.stdout = self.writer; return self
    def __exit__(self, *_)      : sys.stdout = self.old


def _enable_ansi_in_windows():
    # Only on real Windows consoles
    if os.name != "nt":
        return

    kernel32 = ctypes.windll.kernel32
    h_out   = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    mode    = ctypes.c_uint()
    if not kernel32.GetConsoleMode(h_out, ctypes.byref(mode)):
        return
    # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    kernel32.SetConsoleMode(h_out, mode.value | 0x0004)
# -------------------------------------------------------------------
# Call it once, immediately when the module is loaded:
_enable_ansi_in_windows()