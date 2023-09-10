import click

from deploy import deploy
from build import build

# from service import commands as service

@click.group()

def entry_point():
    pass


if __name__ == '__main__':
    entry_point.add_command(deploy)
    entry_point.add_command(build)
    # entry_point.add_command(service.service)
    entry_point()

def cli_entry():
    entry_point.add_command(deploy)
    entry_point.add_command(build)
    entry_point()