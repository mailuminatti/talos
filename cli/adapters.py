
import docker
import os
from loguru import logger

class Adapter:
    pass

class SCA(Adapter):
    def __init__(self, talos_config: dict):
        self.talos_config = talos_config
    
    def run_sca(self, talos_config: dict) -> bool:
        
        logger.info('Running SCA')
        
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
        for log_line in container.logs(stream=True, follow=True): # type: ignore
            print(log_line.decode('utf-8').strip())  # Decode and print each log line

        # Wait for the container to finish and capture the exit code
        exit_code = container.wait()['StatusCode'] # type: ignore
        
        # Remove the container when you're done
        container.remove() # type: ignore
        
        if exit_code==0:
            logger.info('Finnished Running SCA')
            return True
        else:
            logger.error('Finished running SCA with errors')
            return False
