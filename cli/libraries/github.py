import subprocess
from github import Github

# TODO redo this implementing Github library or 'requests'


def get_variable_value(talos_config: object, variable_name: str) -> str:
    
    output = subprocess.check_output(f"gh api -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2022-11-28'   /orgs/{organization}/actions/variables", shell=True)
    output = output