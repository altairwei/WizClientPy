import click

from wizclientpy.sync import require_login


@click.command()
@click.pass_context
def apitest(ctx):
    require_login()
