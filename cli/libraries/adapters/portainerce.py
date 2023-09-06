import requests
import json
from yaspin import yaspin

from libraries.controllers import ci
from libraries.controllers import repository
import sys

sys.path.append(".")



def get_portainer_jwt(talos_config: dict) -> str:
    session = requests.Session()

    portainer_url = talos_config['deployment']['target']['portainer_url']
    portainer_username = talos_config['deployment']['target']['portainer_username']
    portainer_password = talos_config['deployment']['target']['portainer_password']

    # Login to portainer
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
        raise Exception("Failed to login to Portainer")
    
    return token

def does_stack_exist(talos_config) -> bool:
    # Create a session to handle authentication

    session = requests.Session()
    jwt = get_portainer_jwt(talos_config)
    
    portainer_url = talos_config['deployment']['target']['portainer_url']
   
    # Get a list of stacks
    stacks_url = f"{portainer_url}/api/stacks"
    head = {'Authorization': 'Bearer {}'.format(jwt)}
    response = session.get(stacks_url, headers=head)
    
    
    if response.status_code != 200:
        print("Failed to fetch stack information from Portainer.")
        raise Exception("Failed to fetch stack information from Portainer.")
    
    response_string = response.content.decode('utf-8')
    stacks = json.loads(response_string)
    

    # Search for the stack in the stacks available in portainer-ce
    stack_present = next((item for item in stacks if item["Name"] == talos_config['name']), None)
    
    if stack_present != None:
        return True
    else:
        return False

def get_stack_id(talos_config) -> int:

    # Create a session to handle authentication

    session = requests.Session()
    jwt = get_portainer_jwt(talos_config)
    
    portainer_url = talos_config['deployment']['target']['portainer_url']
   
    # Get a list of stacks
    stacks_url = f"{portainer_url}/api/stacks"
    head = {'Authorization': 'Bearer {}'.format(jwt)}
    response = session.get(stacks_url, headers=head)
    
    
    if response.status_code != 200:
        print("Failed to fetch stack information from Portainer.")
        raise Exception("Failed to fetch stack information from Portainer.")
    
    response_string = response.content.decode('utf-8')
    stacks = json.loads(response_string)
    

    # Search for the stack in the stacks available in portainer-ce
    stack_present = next((item for item in stacks if item["Name"] == talos_config['name']), None)
    
    if stack_present != None:
        return stack_present['Id']
    else:
        return 0

def create_stack(talos_config) -> bool:
    session = requests.Session()
    jwt = get_portainer_jwt(talos_config)

    portainer_url = talos_config['deployment']['target']['portainer_url']

    create_stack_url = f"{portainer_url}/api/stacks"
    
    request_body = {
                    "name": talos_config['name'],
                    "repositoryURL": repository.get_repo_url(talos_config),
                    "repositoryAuthentication": True,
                    "repositoryUsername":  talos_config['repository']['repository_username'],
                    "repositoryPassword": talos_config['repository']['repository_password'],
                    "repositoryReferenceName": talos_config['repository']['repository_reference_name'],
    }
    
    params = {'endpointId': talos_config['deployment']['target']['portainer_endpoint_id'], 'type': 2, 'method': 'repository'}

    # Create Stack
    
    head = {'Authorization': 'Bearer {}'.format(jwt)}
    response = session.post(create_stack_url, headers=head, params=params, json=request_body)
    
    success = does_stack_exist(talos_config)
    
    if response.status_code != 200:
        print("Failed to create stack in Portainer.")
        raise Exception("Failed to create stack in Portainer")
    
    return success

def update_stack(talos_config) -> bool:
    
    spinner = yaspin(text="Updating Stack", color="yellow")
    spinner.start()    
    
    stackid = get_stack_id(talos_config)
    
    session = requests.Session()
    jwt = get_portainer_jwt(talos_config)

    portainer_url = talos_config['deployment']['target']['portainer_url']

    # Update a stack's Git configs     
    update_stack_url = f"{portainer_url}/api/stacks/{stackid}/git"   
   
    
    request_body = {
                    "repositoryAuthentication": True,
                    "repositoryUsername":  talos_config['repository']['repository_username'],
                    "repositoryPassword": talos_config['repository']['repository_password'],
                    "repositoryReferenceName": talos_config['repository']['repository_reference_name'],
    }
    
    params = {'endpointId': talos_config['deployment']['target']['portainer_endpoint_id']}

    head = {'Authorization': 'Bearer {}'.format(jwt)}
    response = session.post(update_stack_url, headers=head, params=params, json=request_body)
    
    if response.status_code != 200:
        spinner.fail("❌")
        print("Failed to update stack in Portainer.")
        raise Exception("Failed to update stack in Portainer")
    else:
        spinner.ok("✅")

    # Force redeploy 
    spinner = yaspin(text="Deploying Stack", color="yellow")
    spinner.start()
    deploy_stack_url = f"{portainer_url}/api/stacks/{stackid}/git/redeploy"   
   
    
    request_body = {
                    "pullImage": False,
                    "repositoryAuthentication": True,
                    "repositoryUsername":  talos_config['repository']['repository_username'],
                    "repositoryPassword": talos_config['repository']['repository_password'],
                    "repositoryReferenceName": talos_config['repository']['repository_reference_name'],
    }
    
    params = {'endpointId': talos_config['deployment']['target']['portainer_endpoint_id']}

    head = {'Authorization': 'Bearer {}'.format(jwt)}
    response = session.put(deploy_stack_url, headers=head, params=params, json=request_body)
    
    if response.status_code != 200:
        spinner.fail("❌")
        print("Failed to deploy stack in Portainer.")
        raise Exception("Failed to deploy stack in Portainer")
        return False    
    else:
        spinner.ok("✅")
        return True