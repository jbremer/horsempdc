# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from horsempdc.abstract import MPD
from horsempdc.jsonrpc import JsonRPC


class MopidyClient(MPD):
    def __init__(self, host):
        if ':' in host:
            host, port = host.split(':')
        else:
            port = 6680

        self.jsonrpc = JsonRPC('http://%s:%s/mopidy/rpc' % (host, port))
