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
from http.client import responses
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers import get_lexer_for_mimetype

from wizclientpy.sync.kmserver import WizKMAccountsServer
from wizclientpy.sync.token import WizToken
from wizclientpy.constants import WIZNOTE_HOME_DIR, WIZNOTE_HOME
from wizclientpy.errors import InvalidUser, InvalidPassword
from wizclientpy.utils.urltools import buildCommandUrl, highlightSyntax, formatHeaderField
from wizclientpy.utils.msgtools import error, warning, success


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
        click.echo(error("User `%s` does not exist!" % user_id))
    except InvalidPassword:
        click.echo(error("Password of `%s` is not correct!" % user_id))
    else:
        info = token.userInfo()
        ctx.obj["token"] = token
        # Greetings
        click.echo(success("Hello '{name}' !".format(name=info.strDisplayName)))


@wizcli.command()
@click.pass_context
@click.option("-s", "--show-request", is_flag=True,
              help="Display request before response.")
@click.option(
    "-j", "--json", "content_type", default=True, flag_value='json',
    help="Data items from the command line are serialized as a JSON object.")
@click.option(
    "-f", "--form", "content_type", flag_value='form',
    help="Data items from the command line are serialized as form fields.")
@click.argument("method", nargs=1)
@click.argument("url_command", nargs=1)
@click.argument("request_item", nargs=-1)
def http(ctx, content_type, show_request, method, url_command, request_item):
    """This tool is used to debug server APIs."""
    # determing http method
    method = method.upper()
    try:
        token = ctx.obj["token"]
    except KeyError:
        click.echo(warning("You should login first!"))
    else:
        # Construct url
        info = token.userInfo()
        server = info.strKbServer
        strToken = token.token()
        strUrl = buildCommandUrl(server, url_command, strToken)
        # Collect payload from commandline
        payload = {}
        for item in request_item:
            kvalue = item.split("=")
            if len(kvalue) == 2:
                payload[kvalue[0]] = kvalue[1]
        # Response from server
        if method == "GET":
            res = requests.get(strUrl, params=payload)
        elif method == "POST":
            if content_type == "json":
                payload = json.dumps(payload)
            res = requests.post(strUrl, data=payload)
        else:
            res = requests.request(method, strUrl)
        # Display response
        try:
            # format json string
            body = json.dumps(res.json(), indent=2, separators=(',', ': '))
        except ValueError:
            body = res.text
        # Format and highlight content
        body = highlightSyntax(body, res.headers['content-type'].split(";")[0])
        if show_request:
            click.echo("-------------------REQUEST-------------------")
            click.echo('{request_line}\r\n{header_field}\r\n\r\n{body}'.format(
                request_line=click.style(
                    '%s %s' % (res.request.method, res.request.url),
                    fg="blue"),
                header_field=formatHeaderField(res.request.headers.items()),
                body=res.request.body))
            click.echo("\r\n")
        click.echo("-------------------RESPONSE-------------------")
        click.echo('{status_line}\r\n{header_field}\r\n\r\n{body}'.format(
            status_line=click.style(
                'HTTP/1.1 ' + str(res.status_code) + ' ' +
                responses[res.status_code],
                fg="blue"),
            header_field=formatHeaderField(res.headers.items()),
            body=body))


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
