import json
from typing import Dict, Any

import requests

from wizclientpy import __version__
from wizclientpy.errors import *


def exec_request(
        method: str, url: str, body: Dict[str, Any] = None,
        params: Dict[str, Any] = None, token: str = None):
    """Wrap response for wiznote server request."""
    headers = {'user-agent': 'wizcli/%s' % __version__}
    if token:
        headers['X-Wiz-Token'] = token
    response = requests.request(method, url, json=body, params=params)
    # Raise normal http error.
    response.raise_for_status()
    # Raise WizNote server related error.
    result = None
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
        result = res_json["result"] if "result" in res_json else res_json
    except ValueError:
        result = response.text

    return result
