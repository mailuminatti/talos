import requests
import json
from yaspin import yaspin
import core
import adapters
import git

class Controller:
    pass

#Use the Person class to create an object, and then execute the printname method:

class Builder(Controller):
  def __init__(self, talos_config: dict):
    self.talos_config = talos_config

    def build(self) -> bool:

        success = False

        if 'sca' in self.talos_config['build']:
            sca_adapter = adapters.SCA(self.talos_config)
            result = sca_adapter.run_sca(self.talos_config)

        return success


class DeploymentTarget(Controller):
  def __init__(self, talos_config: dict):
    self.talos_config = talos_config

    def does_stack_exists(self) -> bool:

        stack_exists = False
        
        if self.talos_config['deployment']['target']['name'] == 'portainerce':
            
            deployment_target = PortainerCETarget(self.talos_config)

            stack_exists = deployment_target.does_stack_exists()

        return stack_exists
        
    def update_stack(self) -> bool:
    
        success = False

        if self.talos_config['deployment']['target']['name'] == 'portainerce':
            
            deployment_target = PortainerCETarget(self.talos_config)

            success = deployment_target.update_stack()

        return success

    def create_stack(self) -> bool:
    
        success = False

        if self.talos_config['deployment']['target']['name'] == 'portainerce':
            
            deployment_target = PortainerCETarget(self.talos_config)

            success = deployment_target.create_stack()

        return success

class PortainerCETarget(DeploymentTarget):

    def does_stack_exists(self) -> bool:
    
    # Create a session to handle authentication

        session = requests.Session()
        jwt = self.get_portainer_jwt()
        
        portainer_url = self.talos_config['deployment']['target']['portainer_url']
    
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
        stack_present = next((item for item in stacks if item["Name"] == self.talos_config['name']), None)
        
        if stack_present != None:
            return True
        else:
            return False

    def get_portainer_jwt(self) -> str:

    
        session = requests.Session()

        portainer_url = self.talos_config['deployment']['target']['portainer_url']
        portainer_username = self.talos_config['deployment']['target']['portainer_username']
        portainer_password = self.talos_config['deployment']['target']['portainer_password']

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

    def get_stack_id(self) -> int:

        # Create a session to handle authentication

        session = requests.Session()
        jwt = self.get_portainer_jwt()
        
        portainer_url = self.talos_config['deployment']['target']['portainer_url']
    
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
        stack_present = next((item for item in stacks if item["Name"] == self.talos_config['name']), None)
        
        if stack_present != None:
            return stack_present['Id']
        else:
            return 0

    def update_stack(self) -> bool:
        
        spinner = yaspin(text="Updating Stack", color="yellow")
        spinner.start()    
        
        stackid = self.get_stack_id()
        
        session = requests.Session()
        jwt = self.get_portainer_jwt()

        portainer_url = self.talos_config['deployment']['target']['portainer_url']

        # Update a stack's Git configs     
        update_stack_url = f"{portainer_url}/api/stacks/{stackid}/git"   
    
        
        request_body = {
                        "repositoryAuthentication": True,
                        "repositoryUsername":  self.talos_config['repository']['repository_username'],
                        "repositoryPassword": self.talos_config['repository']['repository_password'],
                        "repositoryReferenceName": self.talos_config['repository']['repository_reference_name'],
        }
        
        params = {'endpointId': self.talos_config['deployment']['target']['portainer_endpoint_id']}

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
                        "repositoryUsername":  self.talos_config['repository']['repository_username'],
                        "repositoryPassword": self.talos_config['repository']['repository_password'],
                        "repositoryReferenceName": self.talos_config['repository']['repository_reference_name'],
        }
        
        params = {'endpointId': self.talos_config['deployment']['target']['portainer_endpoint_id']}

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

    def create_stack(self) -> bool:

        session = requests.Session()
        jwt = self.get_portainer_jwt()

        portainer_url = self.talos_config['deployment']['target']['portainer_url']

        create_stack_url = f"{portainer_url}/api/stacks"
        
        request_body = {
                        "name": self.talos_config['name'],
                        "repositoryURL": core.get_repo_url(self.talos_config),
                        "repositoryAuthentication": True,
                        "repositoryUsername":  self.talos_config['repository']['repository_username'],
                        "repositoryPassword": self.talos_config['repository']['repository_password'],
                        "repositoryReferenceName": self.talos_config['repository']['repository_reference_name'],
        }
        
        params = {'endpointId': self.talos_config['deployment']['target']['portainer_endpoint_id'], 'type': 2, 'method': 'repository'}

        # Create Stack
        
        head = {'Authorization': 'Bearer {}'.format(jwt)}
        response = session.post(create_stack_url, headers=head, params=params, json=request_body)
        
        success = self.does_stack_exists()
        
        if response.status_code != 200:
            print("Failed to create stack in Portainer.")
            raise Exception("Failed to create stack in Portainer")
        
        return success

class Repository(Controller):
    def __init__(self, talos_config: dict):
        self.talos_config = talos_config

    def create_repository(self, talos_config: dict) -> bool:
        return False

class GithubRepository(Repository):
    def create_repository(self, talos_config: dict) -> bool:
        


