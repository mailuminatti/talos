import click

from beat import commands as beat
from init import commands as init

@click.group()
def entry_point():
    pass

if __name__ == '__main__':
    entry_point.add_command(beat.version)
    entry_point.add_command(init.init)
    entry_point()
