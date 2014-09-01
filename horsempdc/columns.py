# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import curses

from horsempdc.abstract import Column


class BandsColumn(Column):
    def __init__(self, bands):
        Column.__init__(self)
        self.populate(bands)

        self.bands = bands

        self.charset = '1234567890qwertyuiop'
        self.line_offset = 2

    def draw(self, focus=True):
        # Alt- combination hotkeys.
        attr = curses.A_REVERSE if focus else 0
        for idx, ch in enumerate(self.charset):
            self.window.addch(self.y + idx, self.x, ch, attr)

        Column.draw(self)

    def handle_alt(self, key):
        # If we're not handling this alt-key combination then we pass it
        # on to our parent class.
        if key not in self.charset:
            Column.handle_alt(key)
            return

        self.scroll(self.offset + self.charset.index(key) - self.index)

    def handle_enter(self):
        albums = self.parent.curse.mpd.albums(self.lines[self.index])

        columns = [
            BandsColumn(self.bands),
            AlbumsColumn(albums),
        ]

        self.parent.curse.new_layout(2, columns)


class AlbumsColumn(Column):
    def __init__(self, albums):
        Column.__init__(self)
        self.populate(albums)
