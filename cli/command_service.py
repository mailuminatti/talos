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
    
    copier.run_copy("cli/copier-talos", "cli")

 


def is_valid_slug(answers, current):
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", current):
        raise inquirer.errors.ValidationError("", reason="That doesn't look like a valid slug") # type: ignore
    else: 
        return True