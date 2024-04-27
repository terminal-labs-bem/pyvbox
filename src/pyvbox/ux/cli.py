import io
import os
import shlex
import shutil
import subprocess
import sys
import tarfile
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
    
def get_file_progress_file_object_class():
    class FileProgressFileObject(tarfile.ExFileObject):
        def read(self, size, *args):
            return tarfile.ExFileObject.read(self, size, *args)
    return FileProgressFileObject

class ProgressFileObject(io.FileIO):
    def __init__(self, path, *args, **kwargs):
        self._total_size = os.path.getsize(path)
        io.FileIO.__init__(self, path, *args, **kwargs)

    def read(self, size):
        progressevent(self.tell(), self._total_size, "bar")
        return io.FileIO.read(self, size)


from time import sleep
def progressbar(v, it, prefix="", size=60, out=sys.stdout):
    count = len(it)
    def show(j):
        x = int(size*j/count)
        print("{}[{}{}] {}/{}".format(prefix, "#"*x, "."*(size-x), j, count), 
                end='\r', file=out, flush=True)
    show(v)

def progressevent(p, t, style):
    if style == "bar":
        progressbar(p, range(t), prefix="", size=60, out=sys.stdout)

def sshquickcall():
    pass

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
      "name": "testvm",
    }
    toml_string = toml.dumps(data)  # Output to a string
    output_file_name = "output.toml"
    with open(output_file_name, "w") as toml_file:
        toml.dump(data, toml_file)

    
@cli.command("up")
def click_up_cmd():
    tarfile.TarFile.fileobject = get_file_progress_file_object_class()
    tar = tarfile.open(fileobj=ProgressFileObject("/home/user/.pyvbox/boxes/platform.tar"))
    tar.extractall("/home/user/.pyvbox/boxes/platform")
    tar.close()
    print("")
    shutil.move("/home/user/.pyvbox/boxes/platform/platform", "/home/user/VirtualBox VMs")
    callshell("vboxmanage registervm '/home/user/VirtualBox VMs/platform/platform.vbox'")
    sleep(5)
    callshell("vboxmanage sharedfolder remove 'platform' --name pyvbox")
    callshell("vboxmanage sharedfolder add 'platform' --name pyvbox --hostpath '/home/user/Desktop/oracle'")
    sleep(5)
    callshell("vboxmanage modifyvm 'platform' --natpf1 'SSH,tcp,127.0.0.1,2522,10.0.2.15,22'")
    sleep(5)
    callshell("vboxmanage startvm platform")
    sleep(5)
    while True:
        sleep(1)
        if callshell("sshpass -p 'fjdksla;' ssh -p 2522 user@127.0.0.1 'ls'"):
            print("ssh seems fine")
            break
    
    callshell("sshpass -p 'fjdksla;' ssh -p 2522 user@127.0.0.1 'sudo mkdir -p /pyvbox'")
    callshell("sshpass -p 'fjdksla;' ssh -p 2522 user@127.0.0.1 'sudo mount -t vboxsf -o uid=1000,gid=1000 pyvbox /pyvbox'")
    command = shlex.split("sshpass -p 'fjdksla;' ssh -p 2522 user@127.0.0.1 'cd /pyvbox; sudo bash provision.sh'")
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    for line in process.stdout:
        sys.stdout.write(str(line, 'utf-8'))

@cli.command("ssh")
def click_ssh_cmd():
    os.system("sshpass -p 'fjdksla;' ssh -p 2522 user@127.0.0.1")
    
@cli.command("destroy")
def click_destroy_cmd():
    callshell("vboxmanage controlvm 'platform' poweroff")
    callshell("vboxmanage unregistervm 'platform' --delete")


@cli.command("halt")
def click_halt_cmd():
    print("halt")
    
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
