# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from __future__ import absolute_import

import logging
import logging.handlers
import os.path

from horsempdc.config import CONFDIR


log = logging.getLogger()


def init_logging(level=logging.INFO):
    formatter = logging.Formatter(
        '%(asctime)s [%(name)s] %(levelname)s: %(message)s')

    log_path = os.path.join(CONFDIR, 'horsempdc.log')
    fh = logging.handlers.WatchedFileHandler(log_path)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    log.setLevel(level)

    # Disable logging for the requests library.
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
