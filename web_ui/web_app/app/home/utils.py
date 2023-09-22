import subprocess

def has_trailing_slash(path):
    return path.endswith('/') or path.endswith('/')



def generate_ssh_configuration(email:str):

    passphrase=""
    ssh_key_name= "ai_ui"
    # Command to create an SSH key pair
    folder_path= "/home/Develop/Confguration/"
    commands= [f'ssh-keygen -t ed25519 -b 4096 -N "{passphrase}" -C "{email}" -f {ssh_key_name}',f"ssh-add ~/{ssh_key_name}"]


    for command in commands:
        try:
        # Run the command in the specified working directory
            subprocess.run(command, shell=True, check=True, cwd=folder_path)
            print("Command executed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")
    

    with open(folder_path + ssh_key_name, 'r') as file:
    # Read the entire file content
        file_content = file.read()
    
        return file_content

    return ""