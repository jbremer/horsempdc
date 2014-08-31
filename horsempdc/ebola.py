# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from __future__ import absolute_import

import curses
import locale
import logging
import time

from horsempdc.art import doge_horse, angry_horse
from horsempdc.exceptions import AngryHorseException, TranquilizerException

locale.setlocale(locale.LC_ALL, '')
LOCALE = locale.getpreferredencoding()

log = logging.getLogger(__name__)


class WalkingHorse(object):
    def __init__(self):
        pass


class Column(object):
    def __init__(self, name):
        self.name = name

        self.pad = None

        self.x = None
        self.y = None
        self.width = None
        self.height = None

        # Current item index.
        self.index = 0

        # List offset from what should be visible in the pad.
        self.offset = 0

    def populate(self, lines):
        self.lines = lines

    def prepare(self):
        if self.pad is None:
            self.pad = curses.newpad(len(self.lines), self.width - 1)

            for idx, line in enumerate(self.lines):
                self.pad.addstr(idx, 0, line.encode(LOCALE))

    def highlight(self, enable=True):
        attr = curses.A_REVERSE if enable else 0
        length = len(self.lines[self.index])
        self.pad.chgat(self.index, 0, length, attr)

    def refresh(self):
        self.pad.refresh(self.offset, 0,
                         self.y, self.x,
                         self.y + self.height - 1,
                         self.x + self.width - 1)

    def draw(self):
        self.refresh()

    def scroll(self, difference):
        # Top of the list.
        if self.index + difference < 0:
            if difference == -1:
                raise AngryHorseException('Top of the list!')

        # End of the list.
        elif self.index + difference >= len(self.lines):
            if difference == 1:
                raise AngryHorseException('End of the list!')

        # Handle this scroll.
        else:
            self.highlight(False)
            self.index += difference
            self.highlight(True)
            self.refresh()


class BandsColumn(Column):
    def __init__(self, name, bands):
        Column.__init__(self, name)
        self.populate(bands)


class Layout(object):
    def __init__(self, window, *columns):
        self.window = window
        self.columns = columns

        self.lines = []
        self.status_line = ''

    def status(self, line, *args):
        # Apply any arguments if given.
        line = line % args if args else line

        # Pad the line until the end of the screen.
        line += ' ' * (self.width - len(line) - 1)

        self.status_line = line

    def active_column(self, index):
        if index >= 0 and index < len(self.columns):
            self.current = self.columns[index]

    def scroll(self, difference):
        self.current.scroll(difference)

    def resize(self):
        self.height, self.width = self.window.getmaxyx()
        self.draw()

    def draw(self):
        self.column_width = self.width / len(self.columns)

        # Horizontal lines. One on top to distinguish the columns, one on the
        # bottom to distinguish the status line.
        self.window.hline(1, 0, curses.ACS_HLINE, self.width)
        self.window.hline(self.height - 2, 0, curses.ACS_HLINE, self.width)

        # Draw each column's name.
        for idx, column in enumerate(self.columns):
            # Initialize this Columns location properties.
            column.y = 2
            column.x = idx * self.column_width
            column.width = self.column_width
            column.height = self.height - column.y - 2

            # Ensure the pad is ready to be used.
            column.prepare()

            self.window.addstr(0, self.column_width * idx,
                               '%d: %s' % (idx + 1, column.name))

        for idx in xrange(1, len(self.columns)):
            # Vertical line to distinguish between the various columns.
            self.window.vline(0, self.column_width * idx - 1,
                              curses.ACS_VLINE, self.height - 2)

            # Plus sign at points where horizontal and vertical lines cross in
            # the menu and "bottom tee" signs where the vertical lines and the
            # status line meet.
            self.window.addch(1, self.column_width * idx - 1, curses.ACS_PLUS)
            self.window.addch(self.height - 2, self.column_width * idx - 1,
                              curses.ACS_BTEE)

        # Highlight whatever is active.
        self.current.highlight()

        # Draw the columns.
        for column in self.columns:
            column.draw()

        # Draw the status line.
        self.window.addstr(self.height - 1, 0, self.status_line)


class Curse(object):
    def __init__(self, bands):
        self._init_ncurses()

        self.columns = {
            'help': Column('help'),
            'playlist': Column('playlist'),
        }

        self.columns['help'].populate(['foo', 'bar', 'help'])
        self.columns['playlist'].populate(['foo', 'bar', 'playlist'])
        self.columns['bands'] = BandsColumn('bands', bands)

        # Callback function that can be used to handle non-blocking events,
        # when .getch() returns "failure", i.e., no keys available.
        self._nonblocking_handler = None

        # Default layout.
        self.layout = Layout(self.stdscr,
                             self.columns['help'],
                             self.columns['playlist'],
                             self.columns['bands'])

        self.layout.active_column(2)

        self.height, self.width = self.stdscr.getmaxyx()

        self._horse_index = 0
        self._status_line = ''

        self.pad_index = 2
        self.list_index = 0

    def _init_ncurses(self):
        # Initialize ncurses and get the main window object.
        self.stdscr = curses.initscr()

        # Enable colors.
        curses.start_color()

        # Don't echo characters right away.
        curses.noecho()

        # Disable buffering - characters are passed through (and available
        # through .getch() right away.)
        curses.cbreak()

        # Let ncurses interpret special keyboard keys.
        self.stdscr.keypad(1)

        # Disable the cursor.
        curses.curs_set(0)

        # Initialize the characters lookup which helps us to resolve special
        # keys, e.g., Page Down, etc. We do this now as most special keys are
        # only available after initscr() has been called.
        self.characters = {
            27: 'alt',
        }

        for key in dir(curses):
            value = getattr(curses, key)
            if key.startswith('KEY_') and isinstance(value, int):
                self.characters[value] = key[4:].lower()

    def finish(self):
        # Nothing special here - just resetting to the original state.
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

    def walking_horse(self):
        lines = doge_horse.split('\n')
        rows = len(lines)
        columns = max(len(line) for line in lines)

        self.redraw()

        # Begin of the horse ride.
        if not self._horse_index:
            self._nonblocking_handler = self.walking_horse
            self.stdscr.nodelay(1)

        # End of the horse ride.
        elif self._horse_index + columns >= self.width:
            self._nonblocking_handler = None
            self.stdscr.nodelay(0)
            return

        extra = [0, 1, 2, 1, 0][self._horse_index % 5]

        for idx, line in enumerate(lines):
            self.stdscr.addstr(self.height - rows - 1 + idx - extra,
                               self._horse_index, line)

        self._horse_index += 2

        self.stdscr.refresh()
        time.sleep(0.1)

    def redraw(self):
        self.stdscr.erase()
        self.stdscr.refresh()
        self.layout.resize()
        self.stdscr.refresh()

    def angry_horse(self, *status_line):
        lines = angry_horse.split('\n')
        rows = len(lines)
        columns = max(len(line) for line in lines)

        self.redraw()

        for idx, line in enumerate(lines):
            x = (self.width - columns) / 2
            y = (self.height - rows) / 2 + idx
            self.stdscr.addstr(y, x, line, curses.A_BOLD)

        self.layout.status(*status_line)
        self.stdscr.refresh()
        time.sleep(0.2)
        self.redraw()
        self.layout.status(*status_line)

    def wait(self):
        # Ensure the screen is entirely up-to-date before entering blocking
        # mode. (Or, at least, normally this will be blocking mode.)
        self.stdscr.refresh()

        ch = self.stdscr.getch()
        if ch < 0:
            # If .getch() returns -1 then we're in non-blocking mode which is
            # only the case when this has been specifically requested. Thus
            # we allow the event to be handled.
            self._nonblocking_handler()
            return

        # Check if we can resolve this character in our mapping and otherwise
        # use the .keyname() function to resolve it.
        ch = self.characters.get(ch, curses.keyname(ch))
        log.debug('Received character %r', ch)

        # Handle this event.
        try:
            if not hasattr(self, '_handle_%s' % ch):
                raise AngryHorseException('Unknown keybinding: %r' % ch)

            getattr(self, '_handle_%s' % ch)()
        except AngryHorseException as e:
            self.angry_horse(e.message)

    def _handle_q(self):
        raise TranquilizerException

    def _handle_alt(self):
        key = self.stdscr.getkey()
        log.debug('alt-%s', key)

    def _handle_resize(self):
        self.layout.resize()

    def _handle_j(self):
        self.layout.scroll(1)

    _handle_down = _handle_j

    def _handle_k(self):
        self.layout.scroll(-1)

    _handle_up = _handle_k

    def _handle_npage(self):
        self.layout.scroll(self.height - 4)

    def _handle_ppage(self):
        self.layout.scroll(-self.height + 4)
