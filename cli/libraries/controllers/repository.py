
def get_repo_url(talos_config: dict) -> str:
    
    if talos_config['repository']['host'] == 'github':
        owner = talos_config['repository']['owner']
        name = talos_config['repository']['name']
        repo_url = f'https://github.com/{owner}/{name}'
        return repo_url    

    else:
        return ''