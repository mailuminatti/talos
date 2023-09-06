from libraries.adapters import github

def get_variable_value(ci_service: str,variable_name: str) -> str:
    
    if ci_service == 'github':
        test_variable = github.get_variable_value('miluminatti-org',variable_name)
        return test_variable
    else:
        return ''
