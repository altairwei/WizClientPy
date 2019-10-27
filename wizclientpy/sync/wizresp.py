from wizclientpy.errors import *


class WizResp:
    """Wrap response and ensure success."""

    def __init__(self, response):
        res_json = response.json()
        return_code = res_json["returnCode"]
        if return_code != 200:
            if return_code == WIZKM_XMLRPC_ERROR_INVALID_USER:
                raise InvalidUser
            if return_code == WIZKM_XMLRPC_ERROR_INVALID_PASSWORD:
                raise InvalidPassword
            if return_code == WIZKM_XMLRPC_ERROR_TOO_MANY_LOGINS:
                raise TooManyLogins
            raise Exception("Unknown server error.")
        self.__json = res_json

    def json(self):
        return self.__json
