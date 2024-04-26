from . import settings
from . import core, app

from .core import initapp, reestablishapp


def main():
    appcontext = core.appcontext
    initapp(appcontext)


def info():
    return "basic info"
