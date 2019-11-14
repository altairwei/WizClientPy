import os
import sqlite3

import click

from wizclientpy.constants import WIZNOTE_HOME


@click.group()
@click.pass_context
@click.option("--user-id", prompt="User Name",
              help="Account name of your WizNote.")
def db(ctx, user_id):
    index_db_file = os.path.join(WIZNOTE_HOME, user_id, "data", "index.db")
    ctx.obj["index_db_file"] = index_db_file


@db.group()
@click.pass_context
def meta(ctx):
    pass


@meta.command(name="get")
@click.pass_context
@click.argument("meta_name", required=False)
@click.argument("meta_key", required=False)
def get_meta(ctx, meta_name, meta_key):
    index_db_file = ctx.obj["index_db_file"]
    with sqlite3.connect(index_db_file) as index_db:
        cursor = index_db.cursor()
        sql_cmd = "select distinct {col} from WIZ_META"
        echo_prefix = ""
        if meta_name:
            meta_name = meta_name.upper()
            sql_cmd += " where META_NAME='%s'" % meta_name
            if meta_key:
                # Query the value of a given meta key
                meta_key = meta_key.upper()
                sql_cmd += " and META_KEY='%s'" % meta_key
                sql_cmd = sql_cmd.format(col="META_VALUE")
            else:
                # Query all meta keys for given meta name
                echo_prefix = "{0}s of {1}: ".format(
                    click.style("META_KEY", fg="blue"), meta_name)
                sql_cmd = sql_cmd.format(col="META_KEY")
        else:
            # Query all meta names
            echo_prefix = "{0}s: ".format(
                click.style("META_NAME", fg="blue"))
            sql_cmd = sql_cmd.format(col="META_NAME")
        cursor.execute(sql_cmd)
        all_rows = cursor.fetchall()
        click.echo(echo_prefix + " ".join(
            row[0] for row in all_rows))


@meta.command(name="set")
@click.pass_context
def set_meta(ctx):
    pass
