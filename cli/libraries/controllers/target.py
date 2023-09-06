
import sys
sys.path.append(".")

from libraries.adapters import portainerce


def does_stack_exist(talos_config: dict) -> bool:
    

    if talos_config['target']['name'] == 'portainerce':
            stack_exist = portainerce.does_stack_exist(talos_config)
            return stack_exist
    else:
        return False

def create_stack(talos_config: dict) -> bool:
    
    if talos_config['target']['name'] == 'portainerce':
            result = portainerce.create_stack(talos_config)
            return result
    else:
        return False

def update_stack(talos_config: dict) -> bool:
    
    if talos_config['target']['name'] == 'portainerce':
            result = portainerce.update_stack(talos_config)
            return result
    else:
        return False