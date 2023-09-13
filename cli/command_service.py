import click
import yaml
import os
import inquirer
import re
from typing import List
import controllers
import core
from yaspin import yaspin

import copier


@click.group()
def service():
    pass

@service.command()
def new():

    if os.path.isfile(f"{os.getcwd()}/talos.yaml"):
        print("A talos.yaml file already exists!")
        raise Exception("A talos.yaml file already exists!")

    click.echo("🚀 Let's create a new service")
    
    # Run questionaire
    copier.run_copy("cli/copier-talos", ".")
    
    with open('.copier-answers.yml', 'r') as file:
        copier_answers = yaml.safe_load(file)

    service_name = copier_answers['service_name']
    
    talos_config = core.load_talos_config(f'{service_name}/talos.yaml')

    
    repo_controller = controllers.Repository(talos_config)
    
    # Create repository
    result = repo_controller.create_repository()
    
    commit = repo_controller.commit_initial_code(copier_answers['service_name'])
    talos_config = talos_config


def is_valid_slug(answers, current):
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", current):
        raise inquirer.errors.ValidationError("", reason="That doesn't look like a valid slug") # type: ignore
    else: 
        return True