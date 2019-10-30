import click


def warning(msg):
    return click.style(msg, fg="yellow")


def error(msg):
    return click.style(msg, fg="red")


def success(msg):
    return click.style(msg, fg="green")
