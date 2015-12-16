# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import json
import logging
import requests


class RPCException(Exception):
    """Generic RPC exception."""


class RPCParseError(RPCException):
    pass


class InvalidRPCRequest(RPCException):
    pass


class RPCInvalidMethod(RPCException):
    pass


class InvalidRPCParameters(RPCException):
    pass


class InternalRPCError(RPCException):
    pass


class RPCServerError(RPCException):
    pass


_CODES = {
    -32700: RPCParseError,
    -32600: InvalidRPCRequest,
    -32601: RPCInvalidMethod,
    -32602: InvalidRPCParameters,
    -32603: InternalRPCError,
}

log = logging.getLogger(__name__)


class JsonRPC(object):
    def __init__(self, url):
        self.url = url

    def query(self, method, **params):
        data = {
            'jsonrpc': '2.0',
            'id': 42,
            'method': method,
            'params': params,
        }

        headers = {
            'content-type': 'application/json',
        }

        try:
            r = requests.post(self.url, data=json.dumps(data),
                              headers=headers).json()
        except Exception as e:
            log.info("Error talking with API: %s", e)
            return []

        if 'error' in r:
            if r['error']['code'] in _CODES:
                raise _CODES[r['error']['code']](r['error']['message'])
            elif r['error']['code'] >= -32000 and r['error']['code'] < 32100:
                raise RPCServerError(r['error']['message'])
            else:
                raise RPCException('Unknown JsonRPC Exception #%d: %s' % (
                    r['error']['code'], r['error']['message']))

        return r['result']
