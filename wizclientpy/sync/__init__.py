import sys

import click
from click import prompt

from wizclientpy.sync.token import WizToken
from wizclientpy.sync.api import WIZNOTE_ACOUNT_SERVER
from wizclientpy.errors import (
    InvalidUser, InvalidPassword, InvalidToken,
    TooManyLogins, ServerXmlRpcError)
from wizclientpy.utils.msgtools import error, warning, success


def require_login(server=None, user_id=None, password=None):
    ctx = click.get_current_context()
    if "token" not in ctx.obj:
        try:
            if not server:
                server = prompt("Server", default=WIZNOTE_ACOUNT_SERVER)
            if not user_id:
                user_id = prompt("User Name")
            if not password:
                password = prompt("Password", hide_input=True)
            token = WizToken(server, user_id, password)
            user_info = token.login()
        except InvalidUser:
            click.echo(error("User `%s` does not exist!" % user_id))
            user_id = prompt("User Name")
            require_login(server=server, user_id=user_id)
        except InvalidPassword:
            click.echo(error("Password of `%s` is not correct!" % user_id))
            password = prompt("Password", hide_input=True)
            require_login(server=server, password=password)
        except click.Abort:
            # cancel login
            return
        else:
            ctx.obj["token"] = token
            ctx.obj["user_info"] = user_info
