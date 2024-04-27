import shlex
import subprocess
import sys
from subprocess import Popen, PIPE

import toml
import click

from .. import settings
from .. import core, app

class OrderCommands(click.Group):
  def list_commands(self, ctx: click.Context) -> list[str]:
    return list(self.commands)

def callshell(cmd):
    command = shlex.split(cmd)
    process = Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode("utf-8").rstrip()

def init():
    app.main()

context_settings = {"help_option_names": ["-h", "--help"]}

@click.group(context_settings=context_settings, cls=OrderCommands)
@click.version_option(
    core.VERSION, "-v", "--version", message=f"{core.PROJECT_NAME}, v{core.VERSION}"
)
@click.pass_context
def cli(ctx):
    init()
    
@cli.command("init")
def click_init_cmd():
    data = {
      "target": {
        "ip": "xx.xx.xx.xx",
        "os": {
          "os": "win 10",
          "Arch": "x64"
        },
        "ports": {
          "ports": ["1", "2"],
          "1": {
            "service": "xxx",
            "ver": "5.9",
          }
        } 
      }
    }
    toml_string = toml.dumps(data)  # Output to a string
    output_file_name = "output.toml"
    with open(output_file_name, "w") as toml_file:
        toml.dump(data, toml_file)

    
@cli.command("up")
def click_up_cmd():
    print("up")
    
@cli.command("down")
def click_down_cmd():
    print("down")
    
@click.group(name="list")
def list_group():
    pass

@list_group.command("vms")
def list_vms_cmd():
    print(callshell("vboxmanage list vms"))

@click.group(name="extra")
def extra_group():
    pass


@extra_group.command("cmd")
def extra_cmd_cmd():
    print("basic cmd")


@click.group(name="system")
def system_group():
    pass


@system_group.command("info")
def system_info_cmd():
    print(app.info())


cli.add_command(list_group)
cli.add_command(extra_group)
cli.add_command(system_group)
