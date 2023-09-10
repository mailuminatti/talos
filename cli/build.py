import click
import os
import yaml
import controllers

@click.group()
def cli_build():
    pass

@click.command()
@click.option('-c','--config', required=False, type=click.Path(exists=True), default='talos.yaml')
def build(config):
    """Runs build steps the application"""


    config_file_path = config
    talos_config = {}
    with open(config_file_path, 'r') as file:
        talos_config = yaml.safe_load(file)
    
    # Check if the application exists in the assigned Target

    if 'build' in talos_config:
        builder = controllers.Builder(talos_config)
        build_result = builder.build()
        
cli_build.add_command(build)
