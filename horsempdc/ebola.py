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

    LOCALE = locale.getpreferredencoding()

    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)
        curses.curs_set(0)

        self.height, self.width = self.stdscr.getmaxyx()

        # Initialize the characters (do it now as most are only available
        # after initscr() has been called.)
        self.characters = {
            27: 'alt',
        }

        for key in dir(curses):
            value = getattr(curses, key)
            if key.startswith('KEY_') and isinstance(value, int):
                self.characters[value] = key[4:].lower()

    def finish(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

    def draw_menu(self, borders=True):
        self.column_width = self.width / len(self.MENU)

        # Horizontal lines. One on top to distinguish the menu, one on the
        # bottom to distinguish the status line.
        if borders:
            self.stdscr.hline(1, 0, curses.ACS_HLINE, self.width)
            self.stdscr.hline(self.height - 2, 0, curses.ACS_HLINE, self.width)

        # Draw each menu.
        for idx, row in enumerate(self.MENU):
            self.stdscr.addstr(0, self.column_width * idx,
                               '%d: %s' % (idx + 1, row))

            # Vertical line to distinguish between the various menus.
            if idx and borders:
                self.stdscr.vline(0, self.column_width * idx - 1,
                                  curses.ACS_VLINE, self.height - 2)

        # Plus sign at points where horizontal and vertical lines cross in
        # the menu and "bottom tee" signs where the vertical lines and the
        # status line meet.
        for idx in xrange(1, len(self.MENU)):
            self.stdscr.addch(1, self.column_width * idx - 1, curses.ACS_PLUS)
            self.stdscr.addch(self.height - 2, self.column_width * idx - 1,
                              curses.ACS_BTEE)

    def _draw_pad(self, index, lines):
        pad = curses.newpad(len(lines), self.column_width - 1)

        for idx, line in enumerate(lines):
            pad.addstr(idx, 0, line.encode(self.LOCALE))

        pad.refresh(0, 0,
                    2, self.column_width * index,
                    self.height - 3, self.column_width * (index + 1) - 1)

        return pad

    def draw_pads(self, bands):
        self.stdscr.refresh()

        self.pads = {
            2: self._draw_pad(2, bands),
        }

    def status(self, line, *args):
        # Apply any arguments if given.
        line = line % args if args else line

        # Pad the line until the end of the screen.
        line += ' ' * (self.width - len(line) - 1)

        self.stdscr.addstr(self.height - 1, 0, line)

    def wait(self):
        self.stdscr.refresh()
        ch = self.stdscr.getch()

        ch = self.characters.get(ch, curses.keyname(ch))
        log.debug('Received character %r', ch)

        if not hasattr(self, '_handle_%s' % ch):
            self.status('Unknown keybinding: %r', ch)
        else:
            getattr(self, '_handle_%s' % ch)()

        self.stdscr.refresh()
