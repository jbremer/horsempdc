# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from __future__ import absolute_import

import curses
import locale
import logging
import time

from horsempdc.art import doge_horse, angry_horse
from horsempdc.exceptions import TranquilizerException

locale.setlocale(locale.LC_ALL, '')
log = logging.getLogger(__name__)


class Curse(object):
    MENU = [
        'help',
        'playlist',
        'bands',
    ]

    LOCALE = locale.getpreferredencoding()

    def __init__(self, bands):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)
        curses.curs_set(0)

        self.lines = {
            2: bands,
        }

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

        self._horse_index = 0
        self._status_line = ''

        self.pad_index = 2
        self.list_index = 0

    def finish(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

    def walking_horse(self):
        lines = doge_horse.split('\n')
        rows = len(lines)
        columns = max(len(line) for line in lines)

        self.redraw()

        # Begin and end of the horse ride.
        if not self._horse_index:
            self.stdscr.nodelay(1)
        elif self._horse_index + columns >= self.width:
            self.stdscr.nodelay(0)
            return

        for idx, line in enumerate(lines):
            self.stdscr.addstr(self.height - rows - 1 + idx,
                               self._horse_index, line)

        self._horse_index += 2

        self.stdscr.refresh()

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

    def _pad_refresh(self, pad, index):
        pad.refresh(0, 0,
                    2, self.column_width * index,
                    self.height - 3, self.column_width * (index + 1) - 1)

    def _draw_pad(self, index, lines):
        pad = curses.newpad(len(lines), self.column_width - 1)

        for idx, line in enumerate(lines):
            pad.addstr(idx, 0, line.encode(self.LOCALE))

        # Highlight line if required.
        if self.pad_index == index:
            pad.chgat(self.list_index, 0,
                      len(self.lines[self.pad_index][self.list_index]),
                      curses.A_REVERSE)

        self._pad_refresh(pad, index)
        return pad

    def draw_pads(self):
        self.stdscr.refresh()

        self.pads_index = {
            2: 0,
        }

        self.pads = {
            2: self._draw_pad(2, self.lines[2]),
        }

    def redraw(self):
        self.stdscr.erase()
        self.draw_menu()
        self.draw_pads()

        self.status(self._status_line)

    def status(self, line, *args):
        # Apply any arguments if given.
        line = line % args if args else line

        # Pad the line until the end of the screen.
        line += ' ' * (self.width - len(line) - 1)

        self._status_line = line
        self.stdscr.addstr(self.height - 1, 0, line)

    def angry_horse(self, *status_line):
        lines = angry_horse.split('\n')
        rows = len(lines)
        columns = max(len(line) for line in lines)

        self.redraw()

        for idx, line in enumerate(lines):
            x = (self.width - columns) / 2
            y = (self.height - rows) / 2 + idx
            self.stdscr.addstr(y, x, line, curses.A_BOLD)

        self.status(*status_line)
        self.stdscr.refresh()
        time.sleep(0.1)
        self.redraw()
        self.status(*status_line)

    def toggle_highlight(self, pad_index, list_index, enable):
        length = len(self.lines[pad_index][list_index])
        attr = curses.A_REVERSE if enable else 0
        self.pads[pad_index].chgat(list_index, 0, length, attr)

    def wait(self):
        self.stdscr.refresh()
        ch = self.stdscr.getch()
        if ch < 0:
            time.sleep(0.10)
            self.walking_horse()
            return

        ch = self.characters.get(ch, curses.keyname(ch))
        log.debug('Received character %r', ch)

        if not hasattr(self, '_handle_%s' % ch):
            self.angry_horse('Unknown keybinding: %r', ch)
        else:
            getattr(self, '_handle_%s' % ch)()

        self.stdscr.refresh()

    def _handle_q(self):
        raise TranquilizerException

    def _handle_alt(self):
        key = self.stdscr.getkey()
        log.debug('alt-%s', key)

    def _handle_resize(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.redraw()

    def _change_list_index(self, old, new):
        self.toggle_highlight(self.pad_index, old, enable=False)
        self.toggle_highlight(self.pad_index, new, enable=True)
        self.list_index = new

        self._pad_refresh(self.pads[self.pad_index], self.pad_index)

    def _handle_j(self):
        if self.list_index == len(self.lines[self.pad_index]):
            self.angry_horse('End of the list!')
            return

        self._change_list_index(self.list_index, self.list_index + 1)

    _handle_down = _handle_j

    def _handle_k(self):
        if not self.list_index:
            self.angry_horse('Top of the list!')
            return

        self._change_list_index(self.list_index, self.list_index - 1)

    _handle_up = _handle_k

    def _handle_npage(self):
        index = min(self.list_index + self.height - 4,
                    len(self.lines[self.pad_index]) - 1)
        self._change_list_index(self.list_index, index)

    def _handle_ppage(self):
        index = max(self.list_index - self.height + 4, 0)
        self._change_list_index(self.list_index, index)
