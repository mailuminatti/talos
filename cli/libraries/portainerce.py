import requests
from libraries import ci
import json

import sys
sys.path.append(".")

from .aux.pyportainer import *

def does_stack_exist(talos_config):
    # Create a session to handle authentication

    user = talos_config['target']['portainer_username']
    password = talos_config['target']['portainer_password']
    endpoint = talos_config['target']['portainer_url']

    p= PyPortainer(endpoint,verifySSL=False)
    p.login(user, password)

    stacks = p.get_stacks(1)

    session = requests.Session()

    portainer_url = talos_config['target']['portainer_url']
    portainer_username = talos_config['target']['portainer_username']
    portainer_password = talos_config['target']['portainer_password']

    # Login to Portainer
    login_url = f"{portainer_url}/api/auth"
    login_payload = {
        "username": portainer_username,
        "password": portainer_password
    }

    response = session.post(login_url, json=login_payload)
    response_string = response.content.decode('utf-8')
    token = json.loads(response_string)['jwt']

    if response.status_code != 200:
        print("Failed to login to Portainer.")
        return False

    # Get a list of stacks
    stacks_url = f"{portainer_url}/api/stacks"
    head = {'Authorization': 'Bearer {}'.format(token)}
    response = session.get(stacks_url, headers=head)
    
    if response.status_code != 200:
        print("Failed to fetch stack information from Portainer.")
        return False
    
    response_string = response.content.decode('utf-8')
    stacks = json.loads(response_string)
    

    # Search for the stack in the stacks available in portainer-ce
    stack_present = next((item for item in stacks if item["Name"] == talos_config['name']), None)
    
    if stack_present != None:
        return True
    else:
        return False

def create_stack(talos_config):
    # Create a session to handle authentication
    session = requests.Session()

    portainer_url = talos_config['target']['portainer_url']
    portainer_username = talos_config['target']['portainer_username']
    portainer_password = talos_config['target']['portainer_password']

    # Login to Portainer
    login_url = f"{portainer_url}/api/auth"
    login_payload = {
        "username": portainer_username,
        "password": portainer_password
    }

    response = session.post(login_url, json=login_payload)
    response_string = response.content.decode('utf-8')
    token = json.loads(response_string)['jwt']

    if response.status_code != 200:
        print("Failed to login to Portainer.")
        return False


    create_stack_url = f"{portainer_url}/stacks/create/standalone/repository"
    {
  "additionalFiles": [
    "[nz.compose.yml",
    " uat.compose.yml]"
  ],
  "autoUpdate": {
    "forcePullImage": false,
    "forceUpdate": false,
    "interval": "1m30s",
    "jobID": "15",
    "webhook": "05de31a2-79fa-4644-9c12-faa67e5c49f0"
  },
  "composeFile": "docker-compose.yml",
  "env": [
    {
      "name": "name",
      "value": "value"
    }
  ],
  "fromAppTemplate": false,
  "name": "myStack",
  "repositoryAuthentication": true,
  "repositoryPassword": "myGitPassword",
  "repositoryReferenceName": "refs/heads/master",
  "repositoryURL": "https://github.com/openfaas/faas",
  "repositoryUsername": "myGitUsername",
  "tlsskipVerify": false
}

  

    # Get a list of stacks
    stacks_url = f"{portainer_url}/api/stacks"
    head = {'Authorization': 'Bearer {}'.format(token)}
    response = session.get(stacks_url, headers=head)
    
    if response.status_code != 200:
        print("Failed to fetch stack information from Portainer.")
        return False
    
    response_string = response.content.decode('utf-8')
    stacks = json.loads(response_string)
    

    # Search for the stack in the stacks available in portainer-ce
    stack_present = next((item for item in stacks if item["Name"] == talos_config['name']), None)
    
    if stack_present != None:
        return True
    else:
        return False