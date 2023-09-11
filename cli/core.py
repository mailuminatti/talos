import yaml
from envyaml import EnvYAML
import os
import re

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