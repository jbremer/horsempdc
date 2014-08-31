# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

class MPD(object):
    def __init__(self, host):
        self.host = host
        self._bands = {}
        self._albums = {}

    def _bands_ordered(self):
        """List of bands ordered as requested - by default alphabetically."""
        return sorted(self._bands.keys())

    def _albums_ordered(self, band):
        """List of albums of a band ordered as requested - by default
        alphabetically."""
        return sorted(self._albums[band].keys())

    def bands(self):
        """Returns a sorted list of all available bands."""
        raise NotImplementedError

    def band(self, name):
        """Returns information about the specified band."""
        raise NotImplementedError
