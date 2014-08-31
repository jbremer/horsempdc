# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import curses


COLORS = dict((v, k) for k, v in {
    curses.COLOR_BLACK: 'black',
    curses.COLOR_RED: 'red',
    curses.COLOR_GREEN: 'green',
    curses.COLOR_YELLOW: 'yellow',
    curses.COLOR_BLUE: 'blue',
    curses.COLOR_MAGENTA: 'magenta',
    curses.COLOR_CYAN: 'cyan',
    curses.COLOR_WHITE: 'white',
})
