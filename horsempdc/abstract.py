# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import curses
import locale

from horsempdc.exceptions import AngryHorseException

locale.setlocale(locale.LC_ALL, '')
LOCALE = locale.getpreferredencoding()


class Column(object):
    COLUMNS = {}

    def __init__(self, name=None):
        self.name = name

        self.window = None
        self.parent = None
        self.pad = None

        self.x = None
        self.y = None
        self.width = None
        self.height = None

        # Offset for reach line. Can be used to prepend each line with
        # an arbitrary string.
        self.line_offset = 0

        # Current item index.
        self.index = 0

        # List offset from what should be visible in the pad.
        self.offset = 0

    def populate(self, lines):
        self.lines = lines
        self.length = len(lines)

    def prepare(self):
        if self.pad is None:
            self.pad = curses.newpad(self.length,
                                     self.width - self.line_offset - 1)

            for idx, line in enumerate(self.lines):
                self.pad.addstr(idx, 0, line.encode(LOCALE))

    def highlight(self, enable=True):
        attr = curses.A_REVERSE if enable else 0
        length = len(self.lines[self.index])
        self.pad.chgat(self.index, 0, length, attr)

    def refresh(self):
        self.pad.refresh(self.offset, 0,
                         self.y, self.x + self.line_offset,
                         self.y + self.height - 1,
                         self.x + self.width - 1)

    def draw(self, focus=True):
        self.refresh()

    def handle_alt(self, key):
        raise AngryHorseException('Unknown combination: alt-%s.' % key)

    def handle_enter(self):
        raise AngryHorseException('This window does not support enter.')

    def scroll(self, difference):
        # Top of the list.
        if self.index + difference < 0:
            if difference == -1:
                raise AngryHorseException('Top of the list!')

            new_index = 0

        # End of the list.
        elif self.index + difference >= self.length:
            if difference == 1:
                raise AngryHorseException('End of the list!')

            new_index = self.length - 1

        # Regular case.
        else:
            new_index = self.index + difference

        # Handle this scroll.
        self.highlight(False)
        self.index = new_index
        self.highlight(True)

        # If the highlighted item is now beyond this screen then we have
        # to update the offset.
        if self.index < self.offset:
            self.offset -= self.height
        elif self.index >= self.offset + self.height:
            self.offset += self.height

        # A bit of boundary checking.
        if self.offset < 0:
            self.offset = 0

        # If there are enough items to cover one or more pages, and we're
        # reaching the last page, then make sure that the last item is
        # actually at the bottom of the page.
        if self.length >= self.height and \
                self.offset >= self.length - self.height:
            self.offset = self.length - self.height

        self.refresh()


class MPD(object):
    def __init__(self, host):
        self.host = host
        self._bands = {}
        self._albums = {}

    def _bands_ordered(self):
        """List of bands ordered as requested - by default alphabetically."""
        return sorted(self._bands.keys())

    def _albums_ordered(self, band):
        """List of albums of a band ordered as requested - by default
        alphabetically."""
        return sorted(self._albums[band].keys())

    def bands(self):
        """Returns a sorted list of all available bands."""
        raise NotImplementedError

    def albums(self, name):
        """Returns a sorted list of all albums for the specified band."""
        raise NotImplementedError
