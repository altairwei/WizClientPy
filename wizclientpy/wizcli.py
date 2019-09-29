#!/usr/bin/env python

import sys
import click
from sync.kmserver import WizKMAccountsServer


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

if __name__ == '__main__':
    wizcli()
