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


@apitest.group(name="ks")
def kb_server():
    pass


@kb_server.command()
@click.pass_context
@click.option('-d', '--with-data', default=False, is_flag=True)
@click.argument("doc_guid")
def download_document(ctx, with_data, doc_guid):
    kb_addr = ctx.obj["user_info"].strKbServer
    kb_guid = ctx.obj["user_info"].strKbGUID
    token = ctx.obj["token"]
    kb_server = KnowledgeBaseServerApi(kb_addr, kb_guid)
    res = kb_server.download_document(doc_guid, token.get(), with_data)
    body_content = json.dumps(res, indent=2, separators=(',', ': '))
    body_content = highlightSyntax(body_content, "application/json")
    click.echo(body_content)
