import os
from dotenv import load_dotenv

def get_env_variable(env_file, variable_name):
    """
    Read the .env file and retrieve the value of the specified variable.

    Parameters:
    env_file (str): Path to the .env file.
    variable_name (str): The name of the variable to retrieve.

    Returns:
    str: The value of the specified variable, or None if not found.
    """
    # Load the .env file
    load_dotenv(env_file)

    # Retrieve the variable value
    return os.getenv(variable_name)

# Example usage:
env_file = '.env'
variable_name = 'CC'
password = get_env_variable(env_file, variable_name)
print(f"The value of {variable_name} is: {password}")
