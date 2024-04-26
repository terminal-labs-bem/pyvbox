import click

from . import settings
from . import core, app


def main() -> int:
    app.main()


def init():
    app.main()


context_settings = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=context_settings)
@click.version_option(
    core.VERSION, "-v", "--version", message=f"{core.PROJECT_NAME}, v{core.VERSION}"
)
@click.pass_context
def cli(ctx):
    init()


@click.group(name="commands")
def commands_group():
    pass


@commands_group.command("cmd")
def cmd_cmd():
    print("basic cmd")


@click.group(name="system")
def system_group():
    pass


@system_group.command("info")
def system_info_cmd():
    print(app.info())


cli.add_command(commands_group)
cli.add_command(system_group)
