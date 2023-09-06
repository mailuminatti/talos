
import docker
import os
from yaspin import yaspin

def run_sca(talos_config: dict) -> bool:
    
    spinner = yaspin(text="Running SCA", color="yellow")
    spinner.start()
    
    failon = 'high'
    if 'failOn' in talos_config['build']['sca']:
        failon = talos_config['build']['sca']['failOn']

    client = docker.from_env()
    container_config = {
        'image': 'anchore/grype',  
        'volumes': {
            f'{os.getcwd()}': {'bind': '/app', 'mode': 'rw'} 
        },
        'command': 'dir:/app --fail-on ' + failon, 
        'network_mode': 'bridge', 
        'detach': True
    }
    # Create and start the container
    container = client.containers.run(**container_config)

    # Stream and display the container logs in real-time
    for log_line in container.logs(stream=True, follow=True):
        print(log_line.decode('utf-8').strip())  # Decode and print each log line

    # Wait for the container to finish and capture the exit code
    exit_code = container.wait()['StatusCode']
    
    # Remove the container when you're done
    container.remove()
    
    if exit_code==0:
        spinner.ok("✅")        
        return True
    else:
        spinner.fail("❌")
        return False
