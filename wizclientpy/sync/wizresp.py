import json

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
