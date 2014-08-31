# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from horsempdc.abstract import MPD
from horsempdc.jsonrpc import JsonRPC


class MopidyClient(MPD):
    def __init__(self, host):
        MPD.__init__(self, host)

        if ':' in self.host:
            host, port = self.host.split(':')
        else:
            port = 6680

        self.jsonrpc = JsonRPC('http://%s:%s/mopidy/rpc' % (host, port))
        self.query = self.jsonrpc.query

    def bands(self):
        if not self._bands:
            rows = self.query('core.library.browse', uri='local:directory')

            for row in rows:
                self._bands[row['name']] = row['uri']

        return self._bands_ordered()

    def albums(self, band):
        rows = self.query('core.library.browse', uri=self._bands[band])
        for row in rows:
            if band not in self._albums:
                self._albums[band] = {}

            self._albums[band][row['name']] = row['uri']

        return self._albums_ordered(band)
