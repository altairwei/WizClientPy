import json

import click

from wizclientpy.utils.urltools import highlightSyntax


def warning(msg):
    return click.style(msg, fg="yellow")


def error(msg):
    return click.style(msg, fg="red")


def success(msg):
    return click.style(msg, fg="green")


def print_json(msg):
    content = json.dumps(msg, indent=2, separators=(',', ': '))
    content = highlightSyntax(content, "application/json")
    click.echo(content)
