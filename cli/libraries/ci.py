from libraries import github

def get_variable_value(ci_service: str,variable_name: str) -> str:
    
    match ci_service:
        case 'github':
            test_variable = github.get_variable_value('miluminatti-org',variable_name)
    # case pattern-2:
    #      action-2
    # case pattern-3:
    #      action-3
    return test_variable