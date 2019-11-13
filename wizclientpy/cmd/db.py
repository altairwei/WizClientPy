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


@db.command()
@click.pass_context
@click.option("-n", "--meta-name", required=False)
@click.option("-k", "--meta-key", required=False)
def meta(ctx, meta_name, meta_key):
    index_db_file = ctx.obj["index_db_file"]
    with sqlite3.connect(index_db_file) as index_db:
        cursor = index_db.cursor()
        sql_cmd = "select META_NAME,META_KEY,META_VALUE from WIZ_META"
        echo_prefix = ""
        col = 0
        if meta_name:
            meta_name = meta_name.upper()
            if meta_key:
                # Query the value of a given meta key
                meta_key = meta_key.upper()
                sql_cmd += " where META_NAME='%s' and META_KEY='%s'" % (
                    meta_name, meta_key)
                col = 2
            else:
                # Query all meta keys for given meta name
                sql_cmd += " where META_NAME='%s'" % meta_name
                echo_prefix = "Existed {0}s of {1}: ".format(
                    click.style("META_KEY", fg="blue"), meta_name)
                col = 1
        else:
            # Query all meta names
            echo_prefix = "Existed {0}s: ".format(
                click.style("META_NAME", fg="blue"))
            col = 0
        cursor.execute(sql_cmd)
        all_rows = cursor.fetchall()
        uniq_vals = set()
        for row in all_rows:
            uniq_vals.add(row[col])
        click.echo(echo_prefix + " ".join(
            val for val in uniq_vals))
