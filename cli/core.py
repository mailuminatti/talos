import yaml
from envyaml import EnvYAML
import os
import re
import string
import random
import git
from loguru import logger
import docker
from pathlib import Path

global feature_flags
feature_flags = []

path_matcher = re.compile(r'\$\{([^}^{]+)\}')

def path_constructor(loader, node):
   ''' Extract the matched value, expand env variable, and replace the match '''
   value = node.value
   match = path_matcher.match(value)
   env_var = match.group()[2:-1] # type: ignore
   return os.environ.get(env_var) + value[match.end():] # type: ignore


def load_talos_config(config_file_path:str) -> dict:
  """Loads the talos_config file from the specified path, but replacing all the environments variables with its value

  Args:
      config_file_path (path): Path to the talos_config file

  Returns:
      dict: The talos_config, with all the environment variables replaced
  """
  yaml.add_implicit_resolver('!path', path_matcher)
  yaml.add_constructor('!path', path_constructor) 
  

  with open(config_file_path, 'r') as file:
    talos_config = yaml.load(file, Loader=yaml.FullLoader)


  return talos_config

def get_repo_url(talos_config: dict) -> str:
  vcs = talos_config['repository']['host']
  owner = talos_config['repository']['owner']
  name = talos_config['repository']['name']
  repo_url = f'https://{vcs}.com/{owner}/{name}'
  return repo_url  

def get_random_string(length: int) -> str:
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def does_repo_exist(vcs: str, owner: str, name: str) -> bool:

  repo_url = f'https://{vcs}.com/{owner}/{name}'

  try:
      folder = get_random_string(8)
      git.Repo.clone_from(repo_url,f'/tmp/{folder}') #type: ignore
      return True
  
  except git.exc.GitError: #type: ignore
      return False

# This creates the talos config object
# not the file
def create_talos_config(answers: dict) -> dict:
   talos_config = {
      'name': answers['service_name'],
      'repository': {
         'host': answers['repository'],
         'owner': answers['owner_name'],
         'name': answers['service_name'],
      },
      'ci': {
         'name': answers['ci']
      },
      'deployments': {
         'target': {
            'name': answers['deployment_target'],
         }
      },
      'build': {
         'dockerlint' : False
      }

   }
   return talos_config

def initialization() -> None:
   
   
   #Check if the Talos home folder exists. If not, it creates it
   talos_home = os.path.join(Path.home(), '.talos')
   
   if not os.path.isdir(talos_home):
      os.mkdir(talos_home)
   
   #If feature_flags file doesnt exists, create it
   with open(os.path.join(talos_home,'feature_flags'), 'a'): pass
   
   #Read the feature_flags file
   with open(os.path.join(talos_home, 'feature_flags'),"r") as f:
      feature_flags = f.read().splitlines()
 
   if 'skip_software_check' not in feature_flags:
      
      if not is_tool('docker'):
         raise Exception('Docker is not installed')
      
      client = get_docker_client()

      try:
         client.containers.list()
      except Exception as e:
         raise Exception("Couldn't connect to Docker socket. Is docker running?")
         
      
      if not is_tool('python3'):
         raise Exception('Python 3 is not installed')

      
      if not is_tool('git'):
         raise Exception('Git is not installed')

      if not is_tool('copilot'):
         raise Exception('Copilot is not installed')
   
   

def is_tool(name):
   """Check whether `name` is on PATH and marked as executable."""
   from shutil import which

   logger.debug(f'Checking if {name} is installed')
   return which(name) is not None

def get_docker_client() -> docker.DockerClient:
      
   user = os.getlogin()
   try:
      client = docker.DockerClient(base_url='unix://var/run/docker.sock')
   except Exception as e:
      client = docker.DockerClient(base_url=f'unix://home/{user}/.docker/desktop/docker.sock')
      
      
   return client