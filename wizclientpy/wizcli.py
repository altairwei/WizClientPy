#!/usr/bin/env python

import sys
import os
import platform
from pathlib import Path

import click
from click_repl import repl
from prompt_toolkit.history import FileHistory

from sync.kmserver import WizKMAccountsServer


if platform.system() == "Windows":
    WIZNOTE_HOME = "WizNote"
elif platform.system() == "Darwin":
    WIZNOTE_HOME = ".wiznote"
elif platform.system() == "Linux":
    WIZNOTE_HOME = ".wiznote"

@click.group()
@click.pass_context
def wizcli(context):
    pass


@wizcli.command()
@click.option("--user-id", prompt="User Name",
              help="Account name of your WizNote.")
@click.option("--password", prompt="Password", hide_input=True,
              help="Password of you WizNote account.")
def login(user_id, password):
    as_server = WizKMAccountsServer()
    if not as_server.login(user_id, password):
        raise Exception("login failed !")
    info = as_server.userInfo
    print("Hello {name} !".format(
        name=info["displayName"]
    ))


@wizcli.command()
def shell():
    prompt_kwargs = {'history': FileHistory(
        str(Path.home().joinpath(WIZNOTE_HOME, ".wizcli_history")))}
    repl(click.get_current_context(), prompt_kwargs=prompt_kwargs)

if __name__ == '__main__':
    # TODO: It's important to deal with Ctrl+C interrupt when writing database.
    wizcli()
