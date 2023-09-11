import click
import yaml
import os
import inquirer
import re
from typing import List
import controllers
import core
from yaspin import yaspin

@click.group()
def service():
    pass

@service.command()
def new():

    if os.path.isfile(f"{os.getcwd()}/talos.yaml"):
        print("A talos.yaml file already exists!")
        raise Exception("A talos.yaml file already exists!")
 


    click.echo("🚀 Let's create a new service")
    
    list_answers = []
    answers = []
    talos_meta = {}
    
    if os.path.exists('meta.yaml'):
        with open('meta.yaml', 'r') as file:
            talos_meta = yaml.safe_load(file)
    
    repository_questions = [

    inquirer.Text('service_name', message="What's the service name?", validate=is_valid_slug),

    inquirer.List('repository',
                    message="Where's the service code going to be hosted?",
                    choices=talos_meta['supported']['repository'],
                    default='github'
                ),

    inquirer.Text('owner_name', message="Who's going to be the owner of the service in {repository}?", validate=is_valid_slug), # type: ignore

    ]
    repository_answers = inquirer.prompt(repository_questions)

    spinner = yaspin(text="Checking availability", color="yellow")
    spinner.start()   

    repo_exists = core.does_repo_exist(
         repository_answers['repository'],
         repository_answers['owner_name'],
         repository_answers['service_name']
    )

    if repo_exists:
        spinner.fail("❌")
        print(f"A repository with name {repository_answers['owner_name']}/{repository_answers['service_name']} already exists")
        raise Exception(f"A repository with name {repository_answers['owner_name']}/{repository_answers['service_name']} already exists")
    else:
        spinner.ok("✅")

    config_questions = [
    
    inquirer.List('ci',
                    message="Where's the CI tool to be used to build the service?",
                    choices=talos_meta['supported']['ci'],
                    default='github'
                ),

    inquirer.List('deployment_target',
                    message="Where's the service going to be deployed?",
                    choices=talos_meta['supported']['deployment']['target'],
                    default='portainerce'
                ),

    inquirer.List('cd',
                message="What's the CD tool to be used to deploy the service?",
                choices=talos_meta['supported']['deployment']['cd'],
                default='github actions'
            ),

    inquirer.Checkbox('build_steps',
                    message="Which steps should be included in the CI? (use space to toggle)",
                    choices=talos_meta['supported']['build_steps'],
                    default=['sca']
                    ),
    ]

    
    config_answers = inquirer.prompt(config_questions)
    
    # Join all the answers
    all_answers = {**repository_answers, **config_answers}
    

    # TODO armar logica de cookiecutter
    print(answers)
    # for answer in answers:
    #     list_answers.append(answer)
        
    talos_config = core.create_talos_config(all_answers)



    talos_config = talos_config

def is_valid_slug(answers, current):
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", current):
        raise inquirer.errors.ValidationError("", reason="That doesn't look like a valid slug") # type: ignore
    else: 
        return True