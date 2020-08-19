import json
from inspect import signature

import click

from wizclientpy.sync import require_login
from wizclientpy.sync.api import AccountsServerApi, KnowledgeBaseServerApi
from wizclientpy.utils.urltools import highlightSyntax


@click.group()
@click.pass_context
def apitest(ctx):
    require_login()


@apitest.group(name="as")
@click.pass_obj
def as_server(obj):
    if "as_server_api" not in obj:
        obj["as_server_api"] = AccountsServerApi()


@as_server.command()
@click.argument("user_name")
@click.argument("password")
def login(user_name, password):
    pass


@apitest.group(name="ks")
@click.pass_obj
def kb_server(obj):
    if "kb_server_api" not in obj:
        obj["kb_server_api"] = KnowledgeBaseServerApi(
            obj["user_info"].kb_server, obj["user_info"].kb_guid)


@kb_server.command()
@click.pass_obj
@click.option('-d', '--with-data', default=False, is_flag=True)
@click.argument("doc_guid")
def download_document(obj, with_data, doc_guid):
    token = obj["token"]
    kb_server = obj["kb_server_api"]
    res = kb_server.download_document(doc_guid, token.get(), with_data)
    body_content = json.dumps(res, indent=2, separators=(',', ': '))
    body_content = highlightSyntax(body_content, "application/json")
    click.echo(body_content)
