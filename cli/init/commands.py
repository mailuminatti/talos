import click
import yaml
import os

# This sys.path.append is done to be able to import libraries from a higher level in the 
# folder structure

import sys
sys.path.append(".")

from libraries.controllers import target

@click.group()
def cli_init():
    pass

@click.command()
def init():

    click.echo('Initializing Talos')

    config_file_path = "talos.yaml"
    
    talos_config = {}
    
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as file:
            talos_config = yaml.safe_load(file)


cli_init.add_command(init)
