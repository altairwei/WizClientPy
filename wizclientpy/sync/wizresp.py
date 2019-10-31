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
                if return_code == WIZKM_XMLRPC_ERROR_INVALID_USER:
                    raise InvalidUser
                if return_code == WIZKM_XMLRPC_ERROR_INVALID_PASSWORD:
                    raise InvalidPassword
                if return_code == WIZKM_XMLRPC_ERROR_TOO_MANY_LOGINS:
                    raise TooManyLogins
                raise Exception("Unknown server error: %s" % json.dumps(res_json))
            self.__json = res_json
        except ValueError:
            self.__text = response.text

    def json(self):
        return self.__json

    def text(self):
        return self.__text
