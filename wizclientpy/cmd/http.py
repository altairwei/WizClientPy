"""
wizcli http is a tool that imitates HTTPie.

It is used to test WizNote server APIs.
"""

import json
from http.client import responses

import click
import requests

from wizclientpy.utils.urltools import (
    buildCommandUrl, highlightSyntax, formatHeaderField)


@click.command()
@click.pass_context
@click.option("-s", "--show-request", is_flag=True,
              help="Display request before response.")
@click.option("--server", help="Provide server address.")
@click.option(
    "-j", "--json", "content_type", default=True, flag_value='json',
    help="Data items from the command line are serialized as a JSON object.")
@click.option(
    "-f", "--form", "content_type", flag_value='form',
    help="Data items from the command line are serialized as form fields.")
@click.option(
    "-t", "--text", "content_type", flag_value='text',
    help="Provide request body with text directly.")
@click.argument("method", nargs=1)
@click.argument("url_command", nargs=1)
@click.argument("request_item", nargs=-1)
def http(
    ctx, server, content_type, show_request, method, url_command,
        request_item):
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
        # TODO: distinguish as or kb server
        if server:
            strServer = server
        else:
            strServer = info.strKbServer
        strToken = token.token()
        strUrl = buildCommandUrl(strServer, url_command, strToken)
        # Collect payload from commandline
        payload = {}
        if content_type == "text":
            # Raw text type item only accept first item
            if request_item:
                payload = request_item[0]
        else:
            # Json and form type item accept key value pair
            for item in request_item:
                kvalue = item.split("=")
                if len(kvalue) == 2:
                    payload[kvalue[0]] = kvalue[1]
            if content_type == "json":
                payload = json.dumps(payload)
        # Response from server
        if method == "GET":
            res = requests.get(strUrl, params=payload)
        elif method == "POST":
            res = requests.post(strUrl, data=payload)
        else:
            res = requests.request(method, strUrl)
        # Display response
        try:
            # format json string
            body_content = json.dumps(
                res.json(),
                indent=2, separators=(',', ': '))
        except ValueError:
            body_content = res.text
        # Format and highlight content
        body_content = highlightSyntax(
            body_content, res.headers['content-type'].split(";")[0])
        if show_request:
            click.echo("-------------------REQUEST-------------------")
            click.echo(
                '{request_line}\r\n{header_field}\r\n\r\n{req_body}'.format(
                    request_line=click.style(
                        '%s %s' % (res.request.method, res.request.url),
                        fg="blue"),
                    header_field=formatHeaderField(
                        res.request.headers.items()),
                    req_body=res.request.body))
            click.echo("\r\n")
        click.echo("-------------------RESPONSE-------------------")
        click.echo('{status_line}\r\n{header_field}\r\n\r\n{req_body}'.format(
            status_line=click.style(
                'HTTP/1.1 ' + str(res.status_code) + ' ' +
                responses[res.status_code],
                fg="blue"),
            header_field=formatHeaderField(res.headers.items()),
            req_body=body_content))
