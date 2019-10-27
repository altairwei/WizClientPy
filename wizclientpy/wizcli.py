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
              help="Password of you WizNote account.")
def login(ctx, user_id, password):
    """
    Login to WizNote server.
    """
    # Avoid being recorded in bash commandline history, password is always
    # asked by hidden prompts.
    token = WizToken(user_id, password)
    try:
        strToken = token.token()
    except InvalidUser:
        click.echo("User `%s` does not exist!" % user_id)
    except InvalidPassword:
        click.echo("Password of `%s` is not correct!" % user_id)
    else:
        info = token.userInfo()
        ctx.obj["user_info"] = info
        ctx.obj["token"] = token
        # Greetings
        click.echo("Hello '{name}' !".format(name=info.strDisplayName))


@wizcli.command()
@click.pass_context
def user(ctx):
    """
    Show user information.
    """
    click.echo(ctx.obj["user_info"])


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
