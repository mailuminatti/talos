import click
import yaml
import os

from envyaml import EnvYAML

# This sys.path.append is done to be able to import libraries from a higher level in the 
# folder structure

import sys
sys.path.append(".")

from libraries.controllers import target
from libraries import core

@click.group()
def cli_init():
    pass

@click.command()
def init():

    click.echo('Initializing Talos')

    config_file_path = "talos.yaml"
    
    if os.path.exists(config_file_path):
        talos_config = core.load_talos_config(config_file_path)

cli_init.add_command(init)
