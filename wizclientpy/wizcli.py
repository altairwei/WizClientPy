#!/usr/bin/env python

import sys
import click


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
    pass

if __name__ == '__main__':
    wizcli()
