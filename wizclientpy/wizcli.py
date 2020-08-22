#!/usr/bin/env python

import sys
import os
import platform
import json
from pathlib import Path

import click
from click_repl import repl
from prompt_toolkit.history import FileHistory
import requests
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers import get_lexer_by_name

from wizclientpy.sync import require_login
from wizclientpy.sync.api import WIZNOTE_ACOUNT_SERVER
from wizclientpy.sync.token import WizToken
from wizclientpy.constants import WIZNOTE_HOME_DIR, WIZNOTE_HOME
from wizclientpy.errors import InvalidUser, InvalidPassword
from wizclientpy.utils.msgtools import error, warning, success
from wizclientpy.cmd.db import db
from wizclientpy.cmd.apitest import apitest


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
              " or https schema.", default=WIZNOTE_ACOUNT_SERVER,
              show_default=True)
@click.option("-a", "--auto-login", is_flag=True,
              help="Automatically login with default user.")
@click.option("-r", "--remember", is_flag=True, help="Remember user name and"
              "password, then set it to default user.")
def login(ctx, user_id, password, server, auto_login, remember):
    """
    Login to WizNote server.
    """
    if auto_login:
        pass
    require_login(server, user_id, password)
    user_info = ctx.obj["user_info"]
    # Greetings
    click.echo(success("Hello '{name}'".format(
        name=user_info.display_name)))


wizcli.add_command(db)
wizcli.add_command(apitest)


@wizcli.command()
@click.argument("keys", nargs=-1)
@click.pass_context
def user(ctx, keys):
    """
    Show user information.

    You can query the value of a given KEYS.
    """
    info = ctx.obj["user_info"]
    if keys:
        for key in keys:
            if key in dir(info):
                click.echo(getattr(info, key))
    else:
        strInfo = str(info)
        lexer = get_lexer_by_name("ini")
        formatter = TerminalFormatter()
        click.echo(highlight(strInfo, lexer, formatter))


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
