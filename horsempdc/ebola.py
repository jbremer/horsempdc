# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import curses
import logging
import time

from horsempdc.abstract import Column
from horsempdc.art import load_ascii_art
from horsempdc.columns import BandsColumn
from horsempdc.exceptions import AngryHorseException, TranquilizerException
from horsempdc.exceptions import RemoveHorseHandler

log = logging.getLogger(__name__)


class WalkingHorse(object):
    def __init__(self):
        self.index = 0
        self.window = None
        self.width = None

    def gallop(self):
        return [0, 1, 2, 1, 0][self.index % 5]

    def draw(self):
        rows, columns, lines = load_ascii_art('doge-horse')

        height, _ = self.window.getmaxyx()

        # End of the horse ride.
        if self.index >= self.width:
            raise RemoveHorseHandler

        for idx, line in enumerate(lines):
            self.window.addstr(height - rows - 2 + idx - self.gallop(),
                               self.index, line[:self.width - self.index])

        self.index += 2

        self.window.refresh()
        time.sleep(0.1)


class Layout(object):
    def __init__(self, curse, *columns):
        self.curse = curse
        self.window = curse.stdscr
        self.columns = columns

        self.lines = []
        self.status_line = ''

        self.current = None
        self.current_index = None

    def status(self, line, *args):
        # Apply any arguments if given.
        line = line % args if args else line

        # Pad the line until the end of the screen.
        line += ' ' * (self.width - len(line) - 1)

        self.status_line = line

    def active_column(self, index):
        if index >= 0 and index < len(self.columns):
            self.current = self.columns[index]
            self.current_index = index

    def scroll(self, difference):
        self.current.scroll(difference)

    def resize(self):
        self.height, self.width = self.window.getmaxyx()
        self.draw()

    def previous_column(self):
        self.current.highlight(enable=False)
        self.current.draw(focus=False)
        self.active_column(self.current_index - 1)
        self.current.highlight(enable=True)
        self.current.draw(focus=True)

    def next_column(self):
        self.current.highlight(enable=False)
        self.current.draw(focus=False)
        self.active_column(self.current_index + 1)
        self.current.highlight(enable=True)
        self.current.draw(focus=True)

    def draw(self):
        self.column_width = self.width / len(self.columns)

        # Horizontal lines. One on top to distinguish the columns, one on the
        # bottom to distinguish the status line.
        self.window.hline(1, 0, curses.ACS_HLINE, self.width)
        self.window.hline(self.height - 2, 0, curses.ACS_HLINE, self.width)

        # Draw each column's name.
        for idx, column in enumerate(self.columns):
            # Initialize this Columns location properties.
            column.window = self.window
            column.parent = self
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
            # self.window.vline(0, self.column_width * idx - 1,
            #                   curses.ACS_VLINE, self.height - 2)

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
            column.draw(self.current == column)

        # Draw the status line.
        self.window.addstr(self.height - 1, 0, self.status_line)


class Curse(object):
    def __init__(self, layout, active_column, mpd):
        self._init_ncurses()

        self.columns = {
            'help': Column('help'),
            'playlist': Column('playlist'),
        }

        self.mpd = mpd

        self.columns['help'].populate(['foo', 'bar', 'help'])
        self.columns['playlist'].populate(['foo', 'bar', 'playlist'])
        self.columns['bands'] = BandsColumn(mpd.bands())

        # Callback function that can be used to handle non-blocking events,
        # when .getch() returns "failure", i.e., no keys available.
        self._nonblocking_handler = None

        columns = []
        for column in layout:
            columns.append(self.columns[column])

        # Stack containing each Layout frame.
        self.stack = []

        # Default layout.
        self.new_layout(active_column, columns)

        self.update_size()

    @property
    def layout(self):
        """Returns the most recent Layout frame."""
        return self.stack[-1]

    def new_layout(self, active_column, columns):
        layout = Layout(self, *columns)
        layout.active_column(active_column - 1)
        self.stack.append(layout)

    def _init_ncurses(self):
        # Initialize ncurses and get the main window object.
        self.stdscr = curses.initscr()

        # Enable colors.
        curses.start_color()

        # Enable transparency.
        curses.use_default_colors()

        # Don't echo characters right away.
        curses.noecho()

        # Disable buffering - characters are passed through (and available
        # through .getch() right away.)
        curses.cbreak()

        # Let ncurses interpret special keyboard keys.
        self.stdscr.keypad(1)

        # Disable the cursor.
        try:
            curses.curs_set(0)
        except:
            pass

        # Initialize the characters lookup which helps us to resolve special
        # keys, e.g., Page Down, etc. We do this now as most special keys are
        # only available after initscr() has been called.
        self.characters = {
            4: 'ctrl_d',
            10: 'enter',
            21: 'ctrl_u',
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

    def install_horse_handler(self, horse):
        self._nonblocking_handler = horse.draw
        horse.window = self.stdscr
        self.stdscr.nodelay(1)

        # TODO Make this a bit more generic. We just don't want the horse to
        # pass by the Bands column.
        _, horse.width = self.stdscr.getmaxyx()
        horse.width = horse.width / 3 * 2

    def redraw(self):
        self.stdscr.erase()
        self.stdscr.refresh()
        self.layout.resize()
        self.stdscr.refresh()

    def update_size(self):
        self.height, self.width = self.stdscr.getmaxyx()

    def angry_horse(self, *status_line):
        # Use the angry horse if there's enough space for it.
        rows, columns, lines = load_ascii_art('angry-horse')

        # Otherwise hope the dumb horse is small enough.
        if rows >= self.height or columns >= self.width:
            rows, columns, lines = load_ascii_art('dumb-horse')

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
            self.redraw()
            try:
                self._nonblocking_handler()
            except RemoveHorseHandler:
                self._nonblocking_handler = None
                self.stdscr.nodelay(0)
            return

        # Check if we can resolve this character in our mapping and otherwise
        # use the .keyname() function to resolve it.
        key = self.characters.get(ch, curses.keyname(ch))
        log.debug('Received character %r (%d)', key, ch)

        # Handle this event.
        try:
            if not hasattr(self, '_handle_%s' % key):
                raise AngryHorseException('Unknown keybinding: %r.' % key)

            getattr(self, '_handle_%s' % key)()
        except AngryHorseException as e:
            self.angry_horse(e.message)

    def _handle_q(self):
        raise TranquilizerException

    def _handle_alt(self):
        key = self.stdscr.getkey()
        self.layout.current.handle_alt(key)

    def _handle_resize(self):
        self.layout.resize()
        self.update_size()

    def _handle_h(self):
        self.layout.previous_column()

    _handle_left = _handle_h

    def _handle_j(self):
        self.layout.scroll(1)

    _handle_down = _handle_j

    def _handle_k(self):
        self.layout.scroll(-1)

    _handle_up = _handle_k

    def _handle_l(self):
        self.layout.next_column()

    _handle_right = _handle_l

    def _handle_npage(self):
        self.layout.scroll(self.height - 4)

    def _handle_ppage(self):
        self.layout.scroll(-self.height + 4)

    def _handle_ctrl_d(self):
        self.layout.scroll((self.height - 4) / 2)

    def _handle_ctrl_u(self):
        self.layout.scroll((-self.height + 4) / 2)

    def _handle_enter(self):
        self.layout.current.handle_enter()
