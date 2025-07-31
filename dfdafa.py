y = self._current_menu._parent._location[0] + self._current_menu._parent._current_index + 1
            for index, item in enumerate(self._current_menu._items.values()):
                if self._current_menu._parent._type == 'H':
                    Terminal.move_to(y,self._current_menu._location[1]-1)
                else:
                    Terminal.move_to(y,self._current_menu._location[1] + self._current_menu._width + 3)

                ctrlkey = f'     Ctrl + {self._current_menu.hotkey}' if self._current_menu.hotkey else ''
                name = item.name + "   ►" if isinstance(item,pyMenu) else item.name
                #self.feedback(f"Name: {name}")
                if item._index == self._current_menu._current_index:
                    sys.stdout.write(
                        f"{ansi['reverse']}{ansi['fg_white']}{ansi['bg_blue']}| "
                        f"{name:<{self._width}}|"
                        f"{ansi['reset']}"
                    )
                else:                
                    sys.stdout.write(
                        f"{ansi['bg_bright_blue']}| "
                        f"{name:<{self._width}}|"
                        f"{ansi['reset']}"
                    )
                y = y + 1
            if self._current_menu._parent._type == 'H':
                Terminal.move_to(y,self._current_menu._location[1]-1)
            else:
                Terminal.move_to(y,self._current_menu._location[1] + self._current_menu._width + 3)
            
            sys.stdout.write(f"{ansi['bg_bright_blue']}\\{'_' * (self._current_menu._width+1)}/")
            sys.stdout.write(f"{ansi['reset']}")
            Terminal.set_cursor_color('blue')
            Terminal.move_to(self._current_menu.y + self._current_menu._current_index +1,self._current_menu.x)
    