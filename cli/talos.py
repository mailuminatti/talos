import click

from command_deploy import deploy
from command_build import build
from command_service import service
from command_flag import flag

import core

from __version__ import __version__ as cliversion

from loguru import logger
import os.path


@click.group()
@click.version_option(cliversion)

def talos():
    core.initialization()
    
    pass
    
talos.add_command(deploy)
talos.add_command(build)
talos.add_command(service)
talos.add_command(flag)

if __name__ == '__main__':
    talos()

def cli_entry():
    talos()
