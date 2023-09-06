import click
import os
import yaml

# This sys.path.append is done to be able to import libraries from a higher level in the 
# folder structure

import sys
sys.path.append(".")

from libraries.controllers import builder

@click.group()
def cli_build():
    pass

@click.command()
def build():
    """Runs build steps the application"""

    config_file_path = "talos.yaml"
    
    talos_config = {}
    
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as file:
            talos_config = yaml.safe_load(file)
    
    # Check if the application exists in the assigned Target

    if 'build' in talos_config:
        build_result = builder.build(talos_config)
        
cli_build.add_command(build)
