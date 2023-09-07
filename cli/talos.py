import click

from beat import commands as beat
from init import commands as init
from deploy import commands as deploy
from build import commands as build
from service import commands as service

@click.group()
def entry_point():
    pass

if __name__ == '__main__':
    entry_point.add_command(beat.version)
    entry_point.add_command(init.init)
    entry_point.add_command(deploy.deploy)
    entry_point.add_command(build.build)
    entry_point.add_command(service.service)
    entry_point()
