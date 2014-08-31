# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

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

    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.wrapper(self.handle_exception)

        self.draw()

    def finish(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

    def handle_exception(self, stdscr):
        log.error('Uncaught exception..')

    def draw_menu(self, x):
        _, width = self.stdscr.getmaxyx()

        for idx, row in enumerate(self.MENU):
            self.stdscr.addstr(0, int(idx * width / len(self.MENU)), row)

        self.stdscr.hline(1, 0, ord('-'), width)

    def draw(self):
        y, x = self.stdscr.getmaxyx()
        self.draw_menu(x)

    def wait(self):
        ch = self.stdscr.getch()
