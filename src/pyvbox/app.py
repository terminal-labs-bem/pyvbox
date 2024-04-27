from . import settings
from . import core, app

from .core import initapp, showapp, reestablishapp


def main():
    appcontext = core.appcontext
    initapp(appcontext)


def info():
    appcontext = core.appcontext
    return showapp(appcontext)
