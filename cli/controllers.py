import requests
import json
from yaspin import yaspin
import core
import adapters
import git
from github import Github
from github import InputGitTreeElement
import os

class Controller:
    pass

#Use the Person class to create an object, and then execute the printname method:

class Builder(Controller):
    def __init__(self, talos_config: dict):
        self.talos_config = talos_config

    def build(self) -> bool:

        success = True
        result_sca = True

        if 'sca' in self.talos_config['build']:
            sca_adapter = adapters.SCA(self.talos_config)
            result_sca = sca_adapter.run_sca(self.talos_config)

        success = success and result_sca
        
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
    def __init__(self, talos_config: dict):
        self.talos_config = talos_config
        
        if 'portainer_username' not in talos_config['deployment']['target']:
            # If portainer_username is not specified, assumes that exists as an environment variable
            talos_config['deployment']['target'].update(
                {'portainer_username': os.environ['PORTAINER_USERNAME']}
                )
        if 'portainer_password' not in talos_config['deployment']['target']:
            # If portainer_password is not specified, assumes that exists as an environment variable
            talos_config['deployment']['target'].update(
                {'portainer_username': os.environ['PORTAINER_PASSWORD']}
                )
        
        
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

    def create_repository(self) -> bool: #type: ignore
        
        success = False

        if self.talos_config['repository']['host'] == 'github':
            
            github_controller = GithubRepository(self.talos_config)
            
            success = github_controller.create_repository()
            
            return success

    def commit_initial_code(self, folder_source_code: str ) -> object: #type: ignore
        
        success = False

        if self.talos_config['repository']['host'] == 'github':
            
            github_controller = GithubRepository(self.talos_config)
            
            success = github_controller.commit_initial_code(folder_source_code)
            
            return success

class GithubRepository(Repository):
    def __init__(self, talos_config: dict):
        self.talos_config = talos_config
        
        if 'repository_username' not in self.talos_config['repository']:
            # If repository_username is not specified, assumes that exists as an environment variable
            self.talos_config['repository'].update(
                {'repository_username': os.environ['REPOSITORY_USERNAME']}
                )

        if 'repository_password' not in self.talos_config['repository']:
            # If repository_password is not specified, assumes that exists as an environment variable
            self.talos_config['repository'].update(
                {'repository_password': os.environ['REPOSITORY_PASSWORD']}
                )

        if 'repository_reference_name' not in self.talos_config['repository']:
            # If repository_reference_name is not specified, assumes that exists as an environment variable
            self.talos_config['repository'].update(
                {'repository_reference_name': 'refs/heads/main'}
                )

    def create_repository(self) -> object:
        """Creates a new repository on GitHub.

        Args:
            talos_config: The object talos_config.

        Returns:
            Success of the operation as a bool.
        """
        g = Github(self.talos_config['repository']['repository_password'])

        try:
            # Create the repository
            repo_name = self.talos_config['repository']['name']
            user = g.get_user()
            repo = user.create_repo(repo_name)
            return repo
        
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False

    def commit_initial_code(self,folder_source_code: str) -> object:
        
        # Commit code from an existing folder
        folder_path = folder_source_code
        branch_name = 'main'
        commit_message = 'Initial commit'

        try:
            g = Github(self.talos_config['repository']['repository_password'])
            user = g.get_user()
            repo_name = self.talos_config['repository']['name']
            repo_owner = self.talos_config['repository']['owner']
            repo_full_name = f"{repo_owner}/{repo_name}"
            repo = user.get_repo(repo_name)
            
            branch = repo.bran
            
            branch = repo.get_branch(branch_name)
            
            # Create a Git tree with the files in the folder
            tree = repo.get_git_tree(branch.commit.sha, recursive=True)
            elements = []
                
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, "rb") as file_content:
                        data = file_content.read()
                    
                    # Create a blob for the file content
                    blob = repo.create_git_blob(data, "base64") #type: ignore

                    # Create a tree element for the file
                    element = InputGitTreeElement(path=file_path, mode="100644", type="blob", sha=blob.sha)
                    elements.append(element)

            # Create a new tree with the elements
            new_tree = repo.create_git_tree(elements)

            # Create a new commit
            parent = repo.get_git_commit(branch.commit.sha)
            commit = repo.create_git_commit(commit_message, new_tree, [parent])

            # Update the branch reference
            ref = repo.get_git_ref(f"heads/{branch_name}")
            ref.edit(commit.sha)

            return True
    
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False