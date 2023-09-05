import click
import yaml
import os

# This sys.path.append is done to be able to import libraries from a higher level in the 
# folder structure

import sys
sys.path.append(".")

from libraries import target

@click.group()
def cli_init():
    pass

@click.command()
def init():

    click.echo('Initializing Talos')

    config_file_path = ["talos.yaml", "talos.yml"]
    config_file_exists = False
    config_file_name = ''
    
    # Iterate through the file names and check if any of them exist
    for file_name in config_file_path:
        if os.path.exists(file_name):
            config_file_exists = True
            config_file_name = file_name
    
    if config_file_exists:
        with open(config_file_name, 'r') as file:
            talos_config = yaml.safe_load(file)
    
    # Check if the application exists in the assigned Target
    app_exists = target.does_stack_exist(talos_config)

    if app_exists:
        print("TODO")
    else:
        result = target.create_stack(talos_config)
    
    talos_config = talos_config


cli_init.add_command(init)
