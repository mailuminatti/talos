
import sys
sys.path.append(".")

from libraries import portainerce


def does_stack_exist(talos_config: object) -> bool:

    match talos_config['target']['name']:
        case 'portainerce':
            stack_exist = portainerce.does_stack_exist(talos_config)
            return stack_exist

def create_stack(talos_config: object) -> bool:

    match talos_config['target']['name']:
        case 'portainerce':
            result = portainerce.create_stack(talos_config)
            return result