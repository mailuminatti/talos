
import sys
sys.path.append(".")

from libraries.adapters import sca

def build(talos_config: dict) -> bool:
    
    result = False
    
    if 'sca' in talos_config['build']:
        result = sca.run_sca(talos_config)
    
    return result
    