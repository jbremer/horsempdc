# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from horsempdc.abstract import Column


class BandsColumn(Column):
    HAS_ALT = True

    def __init__(self, bands):
        Column.__init__(self)
        self.populate(bands)

        self.bands = bands

    def handle_enter(self):
        albums = self.parent.curse.mpd.albums(self.lines[self.index])

        columns = [
            BandsColumn(self.bands),
            AlbumsColumn(albums),
        ]

        self.parent.curse.new_layout(2, columns)


class AlbumsColumn(Column):
    HAS_ALT = True

    def __init__(self, albums):
        Column.__init__(self)
        self.populate(albums)
