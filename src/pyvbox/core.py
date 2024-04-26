import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import sys
import time
import platform
from os import listdir
from os.path import isfile, join
import importlib
import importlib.util
import os
import pipes
import shutil
import urllib
import tempfile
import subprocess
from importlib.metadata import version, metadata
from pathlib import Path, PurePath
from urllib.request import urlopen
from os.path import isdir, dirname, realpath, abspath, join, exists
from zipfile import ZipFile
from configparser import ConfigParser
from copy import deepcopy
from dataclasses import dataclass
import pkg_resources

import psutil

from . import settings
from lowkit.initialization.workingset import setup_workingset


def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, "__dict__"):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


def isWritable(path: str) -> bool:
    try:
        filename = os.path.join(path, "write_test")
        f = open(filename, "w")
        f.close()
        os.remove(filename)
        return True
    except:
        return False


def in_venv():
    return sys.prefix != sys.base_prefix and "VIRTUAL_ENV" in os.environ


def props(cls):
    return [i for i in cls.__dict__.keys() if i[:1] != "_"]


def get_fs_type(mypath):
    root_type = ""
    for part in psutil.disk_partitions():
        if part.mountpoint == "/":
            root_type = part.fstype
            continue

        if mypath.startswith(part.mountpoint):
            return part.fstype

    return root_type


class ImmutableType(type):
    @classmethod
    def change_init(mcs, original_init_method):
        def __new_init__(self, *args, **kwargs):
            if callable(original_init_method):
                original_init_method(self, *args, **kwargs)

            cls = self.__class__

            def raiser(*a):
                raise TypeError("this instance is immutable")

            cls.__setattr__ = raiser
            cls.__delattr__ = raiser
            if hasattr(cls, "__setitem__"):
                cls.__setitem__ = raiser
                cls.__delitem__ = raiser

        return __new_init__

    def __new__(mcs, name, parents, kwargs):
        kwargs["__init__"] = mcs.change_init(kwargs.get("__init__"))
        return type.__new__(mcs, name, parents, kwargs)


class Immutable(metaclass=ImmutableType):
    pass


class AppContext(Immutable):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppContext, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        def get_installed_packages_list():
            installed_packages = pkg_resources.working_set
            installed_packages_list = sorted(
                ["%s==%s" % (i.key, i.version) for i in installed_packages]
            )
            return installed_packages_list

        def get_invocation_cmd():
            full_invocation_cmd = (
                sys.argv[0] + " " + " ".join([pipes.quote(s) for s in sys.argv[1:]])
            )
            if "VIRTUAL_ENV" in os.environ:
                invocation_cmd = full_invocation_cmd.replace(
                    os.environ["VIRTUAL_ENV"] + "/bin/", ""
                )
                return invocation_cmd
            return full_invocation_cmd

        def get_venv_path():
            if "VIRTUAL_ENV" in os.environ:
                return str(os.path.abspath(os.environ["VIRTUAL_ENV"]))
            return "none"

        def get_venvbin_path():
            if "VIRTUAL_ENV" in os.environ:
                return str(os.path.abspath(os.environ["VIRTUAL_ENV"] + "/bin"))
            return "none"

        installed_packages_list = get_installed_packages_list()
        invocation_cmd = get_invocation_cmd()

        import tempfile
        import cpuinfo

        cpudata = cpuinfo.get_cpu_info()
        envstore = deepcopy(os.environ)

        self.app_name = str(invocation_cmd.split(" ")[0])
        self.app_version = str(VERSION)
        self.cwd_is_writable = str(isWritable(os.getcwd()))
        self.root_filesystem = str(get_fs_type("/"))
        self.cpu_type = str(cpudata["brand_raw"])
        self.cpu_arch = str(cpudata["arch"])
        self.number_of_threads = str(psutil.cpu_count())
        self.number_of_physical_cores = str(psutil.cpu_count(logical=False))
        self.number_of_vars_in_env = str(len(envstore))
        self.number_of_bytes_in_env = str(get_size(envstore))
        self.invocation_dir = str(os.path.abspath(os.getcwd()))
        self.invocation_cmd = str(invocation_cmd)
        self.path_to_tempdir = str(os.path.abspath(tempfile.gettempdir()))
        self.path_to_core = str(os.path.abspath(Path(__file__)))
        self.path_to_dottmpdir = str(os.path.abspath(os.getcwd() + "/.tmp"))
        self.running_in_venv = str(in_venv())
        self.path_to_venv = str(get_venv_path())
        self.path_to_venv_bin = str(get_venvbin_path())
        self.soft_path_to_python = str(os.path.abspath(sys.executable))
        self.hard_path_to_python = str(
            os.path.abspath(os.path.realpath(sys.executable))
        )
        self.python_version = str(platform.python_version())
        self.python_details = str(sys.version)
        self.number_of_installed_python_packages = str(len(installed_packages_list))
        self.compiler_toolchain = str(
            "build-essential (libc6-dev | libc-dev, gcc, g++, make, dpkg-dev)"
        )
        self.platform = str(platform.platform())


def initapp(appcontext):
    setup_workingset()
    assert os.path.exists(".tmp")
    assert os.path.exists(os.getcwd() + "/.tmp")
    assert os.path.exists(".tmp/storage")
    assert len(os.listdir(".tmp/storage")) == 10

    from texttable import Texttable

    t = Texttable(max_width=160)
    t.add_rows(
        [
            ["check", "result"],
            ["app name", appcontext.app_name],
            ["app version", appcontext.app_version],
            ["cwd is writable", appcontext.cwd_is_writable],
            ["root filesystem", appcontext.root_filesystem],
            ["cpu type", appcontext.cpu_type],
            ["cpu arch", appcontext.cpu_arch],
            ["number of threads", appcontext.number_of_threads],
            ["number of physical cores", appcontext.number_of_physical_cores],
            ["number of vars in env", appcontext.number_of_vars_in_env],
            ["number of bytes in env", appcontext.number_of_bytes_in_env],
            ["invocation dir", appcontext.invocation_dir],
            ["invocation cmd", appcontext.invocation_cmd],
            ["path to tempdir", appcontext.path_to_tempdir],
            ["path to dottmpdir", appcontext.path_to_dottmpdir],
            ["path to core", appcontext.path_to_core],
            ["running in venv", appcontext.running_in_venv],
            ["path to venv", appcontext.path_to_venv],
            ["path to venv bin", appcontext.path_to_venv_bin],
            ["soft path to python", appcontext.soft_path_to_python],
            ["hard path to python", appcontext.hard_path_to_python],
            ["python version", appcontext.python_version],
            ["python details", appcontext.python_details],
            [
                "number of installed python packages",
                appcontext.number_of_installed_python_packages,
            ],
            ["compiler toolchain", appcontext.compiler_toolchain],
            ["platform", appcontext.platform],
        ]
    )
    print(t.draw())

    ## PYTHONPYCACHEPREFIX
    ## location of site-packages
    ## location of assets dir
    ## location of config.ini (order >> cwd, appworkdir, appdir)
    ## location of appdir
    ## location of srcdir
    ## location of plugins dir
    ## location of infrastructure dir
    ## install method
    ## list plugins
    ## number of shell commands
    ## number of shell envars
    ## is poetry installed
    ## is black installed
    ## is flake8 installed
    ## pretty print time and date of start
    ## number of files in venve dir
    ## logfile locations
    def get_fs_freespace(pathname):
        "Get the free space of the filesystem containing pathname"
        stat = os.statvfs(pathname)
        # use f_bfree for superuser, or f_bavail if filesystem
        # has reserved space for superuser
        return stat.f_bfree * stat.f_bsize

    # print(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
    # print(get_fs_freespace("/")/(1024*1024*1024))
    # print(os.statvfs("/"))
    import subprocess

    # devnull = open(os.devnull,"w")
    # retval = subprocess.call(["dpkg","-s","build-essential"])
    # print(retval)
    # devnull.close()
    # if retval != 0:
    #    print("Package coreutils not installed.")

    # print(tempfile.gettempdir())
    # print(os.path.realpath(sys.executable))

    import subprocess

    ping_response = subprocess.Popen(
        ["/bin/ping", "-c1", "-w100", "8.8.8.8"], stdout=subprocess.PIPE
    ).stdout.read()
    # if b"1 packets transmitted, 1 received, 0% packet loss" in ping_response:
    #    print("ping is good")

    # f = tempfile.TemporaryFile()
    # f.write(b'something on temporaryfile')
    # f.seek(0)
    # print(f.read())
    # f.close()

    # print(psutil.Process().memory_info().rss / (1024 * 1024))
    # print(psutil.virtual_memory().available/(1024*1024))
    # print(platform.freedesktop_os_release())
    # print(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
    # print(time.time() - settings.starttime)
    output = [module.__name__ for module in sys.modules.values() if module]
    import importlib

    # for m in output:
    # mod = importlib.machinery.PathFinder().find_module(m)
    # if mod:
    # print(mod.get_filename())
    # else:
    # print(m)
    import dllist

    dls = dllist.dllist()
    dls = sorted(dls)
    # for dl in dls:
    #    print(os.path.abspath(dl))
    for name, values in vars(settings).items():
        if "__" not in name:
            print(name, values)


def reestablishapp():
    os.chdir(appcontext.invocation_dir)
    setup_workingset()


PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
PROJECT_NAME = os.path.basename(PROJECT_ROOT)
PROJECTNAME = PROJECT_NAME.replace("_", "").replace("-", "")
VERSION = version(PROJECT_NAME)

appcontext = AppContext()
attrs = props(appcontext)
for attr in attrs:
    assert isinstance(getattr(appcontext, attr), str)
