import click
import os
import yaml
import controllers
import core
import inquirer 
from pathlib import Path

@click.group()
def cli_flag():
    pass

@click.command()
@click.option('-c','--config', required=False, type=click.Path(exists=True), default='talos.yaml')
def flag(config):
    """Gathers and sets flags to change Talos behaviour"""

    loaded_answers = []
    talos_home = os.path.join(Path.home(),'.talos') 
    
    with open(os.path.join(talos_home, 'feature_flags')) as f:
        loaded_answers = f.read().splitlines()

    question = [
    inquirer.Checkbox(
        "features",
        message="Feature Flags",
        choices=[
            ("Skip validation of required software at startup", "skip_software_check"),
            
        ],
        default=loaded_answers,
    ),
    ]

    feature_flags = inquirer.prompt(question) #type: ignore
    
    with open(os.path.join(talos_home, 'feature_flags'), 'w') as file:
        for feature in feature_flags['features']: #type: ignore
            file.write(f'{feature}\n')
   
        
cli_flag.add_command(flag)
