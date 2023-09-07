import click
import os
import yaml

# This sys.path.append is done to be able to import libraries from a higher level in the 
# folder structure

import sys
sys.path.append(".")

from libraries.controllers import target
from libraries import core

@click.group()
def cli_deploy():
    pass

@click.command()
@click.option('-c','--config', required=False, type=str, default='talos.yaml')
def deploy(config):
    """Deploys the application"""

    config_file_path = config
    
    talos_config = {}
    
    if os.path.exists(config_file_path):
        talos_config = core.load_talos_config(config_file_path)
    
    # Check if the application exists in the assigned Target
    app_exists = target.does_stack_exist(talos_config)

    if app_exists:
        result = target.update_stack(talos_config)
    else:
        result = target.create_stack(talos_config)
    
    talos_config = talos_config

cli_deploy.add_command(deploy)
