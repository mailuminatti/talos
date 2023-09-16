import click

from command_deploy import deploy
from command_build import build
from command_service import service

import core

from __version__ import __version__ as cliversion

from loguru import logger
import os.path


@click.group()
@click.version_option(cliversion)

def talos():
    core.validate_required_software()
    pass

talos.add_command(deploy)
talos.add_command(build)
talos.add_command(service)

if __name__ == '__main__':
    talos()

def cli_entry():
    talos()
