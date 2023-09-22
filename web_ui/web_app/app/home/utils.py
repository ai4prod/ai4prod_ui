import subprocess
from app.conf.conf_handler import configurationHandler

def has_trailing_slash(path):
    return path.endswith('/') or path.endswith('/')



def generate_ssh_configuration(email:str):

    passphrase=""
    ssh_key_name= "ai_ui"
    # Command to create an SSH key pair
    
    commands= [f'ssh-keygen -t ed25519 -b 4096 -N "{passphrase}" -C "{email}" -f {ssh_key_name}',
               f"ssh-add {configurationHandler.base_path_configuration}{ssh_key_name}"]


    for command in commands:
        try:
        # Run the command in the specified working directory
            subprocess.run(command, shell=True, check=True, cwd=configurationHandler.base_path_configuration)
            print("Command executed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")
    

    with open(configurationHandler.base_path_configuration + ssh_key_name+".pub", 'r') as file:
    # Read the entire file content
        file_content = file.read()
    
        return file_content

    return ""