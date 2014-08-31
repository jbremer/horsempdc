# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os

CONFDIR = os.path.join(os.getenv('HOME'), '.horsempdc')

if not os.path.isdir(CONFDIR):
    os.mkdir(CONFDIR)
