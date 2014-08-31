# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from __future__ import absolute_import

import curses
import locale
import logging

locale.setlocale(locale.LC_ALL, '')
log = logging.getLogger(__name__)


class Curse(object):
    MENU = [
        'help',
        'playlist',
        'bands',
    ]

    CHARACTERS = {}
    LOCALE = locale.getpreferredencoding()

    for key in dir(curses):
        value = getattr(curses, key)
        if isinstance(value, (int, long)):
            CHARACTERS[value] = key

    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)
        curses.curs_set(0)

    def finish(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

    def draw_menu(self, borders=True):
        self.height, width = self.stdscr.getmaxyx()

        self.column_width = width / len(self.MENU)

        if borders:
            self.stdscr.hline(1, 0, curses.ACS_HLINE, width)

        for idx, row in enumerate(self.MENU):
            self.stdscr.addstr(0, self.column_width * idx,
                               '%d: %s' % (idx + 1, row))

            if idx and borders:
                self.stdscr.vline(0, self.column_width * idx - 1,
                                  curses.ACS_VLINE, self.height)

        for idx in xrange(1, len(self.MENU)):
            self.stdscr.addch(1, self.column_width * idx - 1, curses.ACS_PLUS)

    def _draw_pad(self, index, lines):
        pad = curses.newpad(len(lines), self.column_width - 1)

        for idx, line in enumerate(lines):
            pad.addstr(idx, 0, line.encode(self.LOCALE))

        pad.refresh(0, 0,
                    2, self.column_width * index,
                    self.height - 1, self.column_width * (index + 1) - 1)

        return pad

    def draw_pads(self, bands):
        self.stdscr.refresh()

        self.pads = {
            2: self._draw_pad(2, bands),
        }

    def wait(self):
        self.stdscr.refresh()
        ch = self.stdscr.getch()
        log.debug('Received character %d (%s)',
                  ch, self.CHARACTERS.get(ch, ch))
