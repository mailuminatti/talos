import click
import yaml
import os
import inquirer
from typing import List

# This sys.path.append is done to be able to import libraries from a higher level in the 
# folder structure

import sys
sys.path.append(".")

from libraries.controllers import target

@click.group()
def cli_service():
    pass

@click.command()
def service():

    click.echo("Alright - Let's create a new service")
    
    list_answers = []
    answers = []
    talos_meta = {}
    
    if os.path.exists('meta.yaml'):
        with open('meta.yaml', 'r') as file:
            talos_meta = yaml.safe_load(file)
    
    questions = [
    inquirer.Text('service_name', message="What's the service name?"),
    inquirer.List('repository',
                    message="Where's the service code going to be hosted?",
                    choices=talos_meta['supported']['repository'],
                ),
    inquirer.List('target',
                    message="Where's the service going to be deployed?",
                    choices=talos_meta['supported']['deployment']['target'],
                ),
    inquirer.List('cd',
                message="What's the CD tool to be used to deploy the service?",
                choices=talos_meta['supported']['deployment']['cd'],
            ),
    inquirer.Checkbox('build_steps',
                    message="Which steps should be included in the CI?",
                    choices=talos_meta['supported']['build_steps'],
                    ),

    ]
    answers = inquirer.prompt(questions)
    
    for answer in answers:
        list_answers.append(answer)
        
    talos_config = {}

cli_service.add_command(service)
