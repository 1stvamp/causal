"""Utilities module, generic utils live here
"""

def get_module_name(name):
    """Get the name of the module given a sub-module within it.
    """
    return name.rpartition('.')[0]

