import json
from typing import Dict, Any

import requests

from wizclientpy import __version__
from wizclientpy.errors import *


class WizResp:
    """Wrap response and ensure success."""

    def __init__(self, response):
        # Raise normal http error.
        response.raise_for_status()
        # Raise WizNote server related error.
        try:
            # Check JSON response
            res_json = response.json()
            return_code = res_json["returnCode"]
            if return_code != 200:
                try:
                    raise CODE_EXCEPTION_MAPPING[return_code]
                except KeyError:
                    raise ServerXmlRpcError(
                        "Unknown server error: %s" % json.dumps(res_json))
            self.__json = res_json
        except ValueError:
            self.__text = response.text

    def json(self):
        """Get the whole json response."""
        return self.__json

    def result(self):
        """Get result key value from json response."""
        if self.__json:
            return self.__json["result"]
        else:
            return {}

    def text(self):
        return self.__text


def json_request(
        method: str, url: str, body: Dict[str, Any] = None,
        token: str = None):
    headers = {'user-agent': 'wizcli/%s' % __version__}
    if token:
        headers['X-Wiz-Token'] = token
    resp = requests.request(method, url, json=body)
    return WizResp(resp).result()
