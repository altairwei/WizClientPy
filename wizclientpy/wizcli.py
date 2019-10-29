#!/usr/bin/env python

import sys
import os
import platform
from pathlib import Path

import click
from click_repl import repl
from prompt_toolkit.history import FileHistory

from wizclientpy.sync.kmserver import WizKMAccountsServer
from wizclientpy.sync.token import WizToken
from wizclientpy.constants import WIZNOTE_HOME_DIR, WIZNOTE_HOME
from wizclientpy.errors import InvalidUser, InvalidPassword
from wizclientpy.utils.urltools import buildCommandUrl


@click.group(invoke_without_command=True)
@click.pass_context
def wizcli(ctx):
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(shell)


@wizcli.command()
@click.pass_context
@click.option("--user-id", prompt="User Name",
              help="Account name of your WizNote.")
@click.option("--password", prompt="Password", hide_input=True,
              help="Password of you WizNote account. WARNING: To avoid"
              " password being recorded in bash commandline history, this"
              " option should not be used in production.")
@click.option("-s", "--server", help="Set address of your account server."
              " Server address can be a pure IP address or prefixed with http"
              " or https schema.")
def login(ctx, user_id, password, server):
    """
    Login to WizNote server.
    """
    if server:
        as_server = WizKMAccountsServer(server)
    token = WizToken()
    token.setUserId(user_id)
    token.setPasswd(password)
    try:
        strToken = token.token()
    except InvalidUser:
        click.echo("User `%s` does not exist!" % user_id)
    except InvalidPassword:
        click.echo("Password of `%s` is not correct!" % user_id)
    else:
        info = token.userInfo()
        ctx.obj["token"] = token
        # Greetings
        click.echo("Hello '{name}' !".format(name=info.strDisplayName))


@wizcli.command()
@click.pass_context
@click.option("-m", "--method", default="GET")
@click.argument("url_command")
def http(ctx, method, url_command):
    # determing http method
    method = method.upper()
    """This tool is used to debug server APIs."""
    # TODO: requre login
    try:
        token = ctx.obj["token"]
    except KeyError:
        click.echo("You should login first!")
    else:
        info = token.userInfo()
        server = info.strKbServer
        strToken = token.token()
        strUrl = buildCommandUrl(server, url_command, strToken)
        print(method, strUrl)


@wizcli.command()
@click.pass_context
def user(ctx):
    """
    Show user information.
    """
    print(ctx.obj["token"].userInfo())


@wizcli.command()
def shell():
    """
    Open an interactive tools, just like a shell.
    """
    prompt_kwargs = {
        'history': FileHistory(
            str(Path(WIZNOTE_HOME).joinpath(".wizcli_history"))),
        'message': u"wizcli>>> "}
    repl(click.get_current_context(), prompt_kwargs=prompt_kwargs)


if __name__ == '__main__':
    # TODO: It's important to deal with Ctrl+C interrupt when writing database.
    wizcli(obj={})
