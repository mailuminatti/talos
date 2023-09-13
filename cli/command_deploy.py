import click
import os
import yaml

# This sys.path.append is done to be able to import libraries from a higher level in the 
# folder structure

import sys
import controllers
import core

@click.command()
@click.option('-c','--config', required=False, type=click.Path(exists=True), default='talos.yaml')
def deploy(config):
    """Deploys the application"""
    click.echo('deploying')
    config_file_path = config    
    talos_config = {}
    
    if os.path.exists(config_file_path):
        talos_config = core.load_talos_config(config_file_path)
    else:
        raise(Exception("Talos file was not found"))
    
    # Check if the application exists in the assigned Target
    
    deployment_target = controllers.DeploymentTarget(talos_config)
    

    app_exists = deployment_target.does_stack_exists()

    if app_exists:
        result = deployment_target.update_stack()
    else:
        result = deployment_target.create_stack()

    return result

