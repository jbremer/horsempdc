# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from __future__ import absolute_import

import curses
import logging

log = logging.getLogger(__name__)


class Curse(object):
    MENU = [
        'help',
        'playlist',
        'browse',
        'search',
        'library',
    ]

    CHARACTERS = {}

    for key in dir(curses):
        value = getattr(curses, key)
        if isinstance(value, (int, long)):
            CHARACTERS[value] = key

    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)

        self.draw_menu()

    def finish(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

    def draw_menu(self, borders=True):
        height, width = self.stdscr.getmaxyx()

        if borders:
            self.stdscr.hline(1, 0, curses.ACS_HLINE, width)

        for idx, row in enumerate(self.MENU):
            offset = int(idx * width / len(self.MENU))
            self.stdscr.addstr(0, offset, '%d: %s' % (idx + 1, row))

            if idx and borders:
                self.stdscr.vline(0, offset - 1, curses.ACS_VLINE, height)

    def wait(self):
        self.stdscr.refresh()
        ch = self.stdscr.getch()
        log.debug('Received character %d (%s)',
                  ch, self.CHARACTERS.get(ch, ch))
