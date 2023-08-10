from atlassian.bitbucket import Cloud
import requests
import git
import subprocess
from pathlib import Path
import sys
import os
import shutil






class BicbucketConnection():
    """
    See this to understand how to setup connection
    https://community.atlassian.com/t5/Bitbucket-questions/Cant-connect-bitbucket-using-python-stashy/qaq-p/1943536
    :param username
    :param password

    """

    def __init__(self,
                 username: str,
                 password: str,
                 repo_name: str,
                 workspace_name: str
                 ) -> None:

        self.bitbucket = Cloud(
            username=username,
            password=password,
            cloud=True)

        self.repo_name = repo_name
        self.workspace_name = workspace_name

    def get_all_projects(self,
                         workspace_name: str):

        projects = iter(self.bitbucket.workspaces.get(
            workspace_name).projects.each())
        # print the first one
        print(next(projects))

    def handle_connection_excpetion(self,
                                    request_url: str,
                                    json_parmas: dict):

        try:
            response = self.bitbucket.post(request_url, json_parmas)
            print("REPO CREATED")
            return response

        except requests.exceptions.HTTPError as http_error:
            print(f"HTTP Error: {http_error}")
        except requests.exceptions.RequestException as request_exception:
            print(f"Request Exception: {request_exception}")

    def create_repository(self,
                          repo_description: str,
                          is_private=True):

        repository_data = {
            "scm": "git",
            "name": self.repo_name,
            "description": repo_description,
            "is_private": is_private
        }

        request_url = f'repositories/{self.workspace_name}/{self.repo_name}'
        params = repository_data
        self.handle_connection_excpetion(request_url, params)


class GitHandler():
    """
    Class used to update git repository locally or remote
    This Class cannot be create a new repository on Bitbucket or Github
    Used BicbucketConnection to create a repository on Bitbucket

    Warning this class can be used for remote handling repo management
    if git is already configure to work with ssh or OAuth token is already
    saved o System (such as storing them in a git configuration file)

    """

    def __init__(self,
                 local_repo_path: str,
                 remote_repo_url) -> None:

        self.repo_name = self.get_last_part_noext(remote_repo_url)

        self.local_repo_path = local_repo_path + self.repo_name
        self.remote_repo_url = remote_repo_url

        self.local_repo = None
        # Check if the repository is present
        if Path(self.local_repo_path).exists():
            self.local_repo = git.Repo(self.local_repo_path)

        self.submodule_list = [
            "https://github.com/ai4prod/data_version_script.git"]

    def get_last_part_noext(self, path):

        file_path = Path(path)
        file_name_without_extension = file_path.stem
        last_part_of_path = Path(file_name_without_extension).name
        return str(last_part_of_path)

    def clone_repository(self):

        repo = git.Repo.clone_from(self.remote_repo_url, self.local_repo_path)
        print(f"Cloned repository to {repo.working_tree_dir}")

        if (self.local_repo is None):
            self.local_repo = git.Repo(self.local_repo_path)

    def push_to_remote(self,
                       remote_name="origin",
                       branch_name="master"):

        remote = self.local_repo.remote(name=remote_name)

        # Push changes to the specified branch
        remote.push(branch_name)

    def push_tag_to_remote(self, tag_version,
                           remote_name="origin",
                           ):
        tag = self.local_repo.tags[tag_version]
        remote = self.local_repo.remote(name=remote_name)
        remote.push(tag)

    def add_update_submodule(self,):

        for submodule in self.submodule_list:
            submodule_name = self.get_last_part_noext(submodule)
            submodule = self.local_repo.create_submodule(
                name=submodule_name, path=submodule_name, url=submodule)
            submodule.update(init=True)

    def add_and_commit(self, commit_message):
        # Add all changes to the index (stage changes)
        self.local_repo.git.add('--all')

        # Commit the changes
        self.local_repo.index.commit(commit_message)

    def add_list_of_files_and_commit(self, file_list: list):

        self.local_repo.index.add(file_list)

    def update_tag(self, tag_version, message):
        tag = self.local_repo.create_tag(
            tag_version, message=message)
        print(tag)


class DvcHandler():

    """
    Class used to Handle dvc Update Push And Pull
    :param local_repo: path to git repository to add Dataset Data
    :param remote_dataset: remote daset location path
    :param ssh_user: remote dataset uder
    :param ssh_pws: remote ssh password
    :param ssh_ip: optional ip value for remote ssh dataset
    """

    def __init__(self,
                 local_repo: str,
                 dvc_remote_path: str,
                 dvc_remote_ssh_user=None,
                 dvc_remote_ssh_psw=None,
                 dvc_remote_ssh_ip=None) -> None:

        self.local_repo = local_repo
        self.dvc_remote_path = dvc_remote_path
        self.dvc_remote_ssh_user = dvc_remote_ssh_user
        self.dvc_remote_ssh_psw = dvc_remote_ssh_psw
        self.dvc_remote_ssh_ip = dvc_remote_ssh_ip

        self.dvc_file_list = []

    def execute_pipeline_commands(self, pipeline):
        output=[]
        for command in pipeline:
            #print(f"-- {' '.join(command)} --")
            result = subprocess.run(
                command, cwd=self.local_repo, capture_output=True, text=True)
            output.append(result.stdout.strip())
        return output

    def setup_remote(self,):

        if(self.dvc_remote_ssh_user is not None):
            return [
                ["dvc", "remote", "add", "--default", "ssh-storage",
                    f"ssh://{self.dvc_remote_ssh_ip}/{self.dvc_remote_path}"],
                ["dvc", "remote", "modify", "ssh-storage",
                    "user", f"{self.dvc_remote_ssh_user}"],
                ["dvc", "remote", "modify", "ssh-storage", "port", "22"],
                ["dvc", "remote", "modify", "ssh-storage", "port", "22"],
                ["dvc", "remote", "modify", "ssh-storage",
                    "password", f"{self.dvc_remote_ssh_psw}"]
            ]
        else:
            Path(self.dvc_remote_path).mkdir(parents=True, exist_ok=True)
            return [
                ["dvc", "remote", "add", "--default",
                    "origin", f"{self.dvc_remote_path}"]
            ]

    def init_git_repo_with_dvc(self):

        first_time_execution_pipeline = [
            ['dvc', 'init'],
            ['dvc', 'add', "Data/Dataset"],
            self.setup_remote()[0]
        ]

        self.execute_pipeline_commands(first_time_execution_pipeline)
        print(first_time_execution_pipeline)

    def update_dataset(self,):
        update_dataset_pipeline = [
            ['dvc', 'add', "Data/Dataset"],
        ]

        self.execute_pipeline_commands(update_dataset_pipeline)
        print("dvc Update Dataset")

    def push_to_remote(self):

        push_dataset_remote = [
            ['dvc', 'push'],
        ]

        self.execute_pipeline_commands(push_dataset_remote)
        print("dvc Update Dataset")
    
    def check_status(self):

        check_pipeline=[
            ["dvc","status"]
        ]
        result=self.execute_pipeline_commands(check_pipeline)

        return True if ("changed" in result[0] or "modified" in result[0]) else False 



class DatasetHandler():

    def __init__(self) -> None:
        self.bitbucket=None
        self.gitHandler=None
        self.dvcHandler=None
        
    """
    This class will implementh method to init and update dataset version
    :param local_repo_path: Path to folder without bitbucket_repository_name for example /Home/Ubuntu/{bitbucket_repository_name}
     bitbucket_repository_name will be added after gitHandler initialization to global local path. This because first i need
     to initialize remote repository.
    :param bibucket_username bitbucket username
    :param bitbucket_password 
    :param bitbucket_repository_name remote repository name
    :param bitbucket_workspace_name remote bitbucket workspace name
    """
    def setup(self,
                local_repo_path: str,
                bibucket_username: str,
                bitbucket_password: str,
                bitbucket_repository_name: str,
                bitbucket_workspace_name: str,
                dvc_remote_path: str,
                dvc_remote_ssh_user=None,
                dvc_remote_ssh_psw=None,
                dvc_remote_ssh_ip=None,
                create_repository=True,
                ) -> None:

        print(bibucket_username)
        
        if (self.bitbucket is not None):
            self.bitbucket=None
        if (self.dvcHandler is not None):
            self.dvcHandler=None
        if (self.gitHandler is not None):
            self.gitHandler=None

        self.bitbucket = BicbucketConnection(username=bibucket_username,
                                            password=bitbucket_password,
                                            repo_name=bitbucket_repository_name,
                                            workspace_name=bitbucket_workspace_name)
        if(create_repository):
            self.bitbucket.create_repository(
                repo_description="create from python")

        # TODO: This is valid for Bitbucket
        remote_repo_url = f"https://{bibucket_username}@bitbucket.org/{bitbucket_workspace_name}/{bitbucket_repository_name}.git"

        self.gitHandler = GitHandler(local_repo_path, remote_repo_url)

        self.dvcHandler = DvcHandler(local_repo=self.gitHandler.local_repo_path,
                                    dvc_remote_path=dvc_remote_path,
                                    dvc_remote_ssh_user=dvc_remote_ssh_user,
                                    dvc_remote_ssh_psw=dvc_remote_ssh_psw,
                                    dvc_remote_ssh_ip=dvc_remote_ssh_ip)
    
    def getCurretFileConfLocation(self, repo_template_name="data_versioning_template"):
        """
        :param task select type of task for example classification. This needs to have the same folder name of the task

        Get current File location
        return current file location and current conf location

        """
        # Set current file path to load config independent from python launch path
        current_exec_path = os.path.abspath(__file__)
        current_location = os.path.dirname(current_exec_path)
        current_repo_location = None
        if sys.platform.startswith('win'):
            current_repo_location = current_location + \
                f"\\{repo_template_name}\\"
        else:
            current_repo_location = current_location + \
                f"/{repo_template_name}/"

        return current_repo_location

    def copyFoldersFromTemplateRepo(self, task_name):
        """
        This function will copy all the necessary folders to init a dataset
        repository

        """
        folders_to_copy = {}
        folders_to_copy[f"/Data/ExampleData/{task_name}"] = "/Data/Dataset/"
        folders_to_copy["/DataTest"] = "/DataTest"
        folders_to_copy["/StreamingDataBuffer"] = "/StreamingDataBuffer"

        files_to_copy = [".gitignore"]
        template_folder_path = self.getCurretFileConfLocation()

        for folders_to_copy_key in folders_to_copy.keys():

            shutil.copytree(template_folder_path + folders_to_copy_key,
                            self.gitHandler.local_repo_path + folders_to_copy[folders_to_copy_key])

        for file in files_to_copy:
            print(self.gitHandler.local_repo_path + file)
            shutil.copy(template_folder_path + file,
                        self.gitHandler.local_repo_path + f"/{file}")

    def initDataset(self,
                    task_name="classification"):
        """
        This function will
        1) Remote Folder must already be created
        2) Clone the remote folder in the local_repo_path
        4) Copy the necessary Folders from https://github.com/ai4prod/data_versioning_template(submodule of ai4prod_gui)into local_repo_path
        5) Update submodule ref of local_repo_path
        6) Local commit 
        7) Update remote to bitbucket repo
        8) Init Dataset Folder with dvc
        9) Update Git files with dvc tracking

        """

        self.gitHandler.clone_repository()
        self.copyFoldersFromTemplateRepo(task_name)
        self.gitHandler.add_update_submodule()
        self.gitHandler.add_and_commit("init dataset")
        self.gitHandler.push_to_remote()
        self.dvcHandler.init_git_repo_with_dvc()
        self.gitHandler.add_and_commit("initialize Data/Dataset with dvc")
        self.gitHandler.push_to_remote()

        # TODO: Salvare a database i parametri del dataset inizializzato
    
    def updateTag(self, tag_version):
        """
        This Function will update tag_version 
        of dataset if new data are present using 
        dvc api python

        Before update tag need to update Dataset with new Data

        """
        self.dvcHandler.update_dataset()
        
        self.gitHandler.add_and_commit(
             f"update dataset to version{tag_version}")
        self.gitHandler.update_tag(tag_version=tag_version,
                                   message=f"update to version {tag_version}",
                                   )
        
        self.gitHandler.push_to_remote()
        self.gitHandler.push_tag_to_remote(tag_version)
        self.dvcHandler.push_to_remote()


datasetHandler= DatasetHandler()

if __name__ == "__main__":

    
    data_file_path = 'C:\\Users\\erict\\OneDrive\\Desktop\\Develop\\test_python\\'
    result = subprocess.run(
                ['dvc', 'status'], cwd=data_file_path, capture_output=True, text=True)

    output=result.stdout.strip()
    
    if "changed" in output or "modified" in output:
        
        input("t")
    #bitbucket= BicbucketConnection(username="",password="")
    # bitbucket.get_all_projects("vedev-2")

    #bitbucket.create_repository("test_python_api","vedev-2","create from python api")
    # gitHandler = GitHandler("C:\\Users\\erict\\OneDrive\\Desktop\\Develop\\",
    #                         "")
    # gitHandler.clone_repository()
    #gitHandler.add_and_commit("commit from python")
    # gitHandler.add_update_submodule()
    # local_repo_path = "C:\\Users\\erict\\OneDrive\\Desktop\\Develop\\"
    # bit_repo_name = "test_python"
    # bit_workspace_name = "vedev-2"

    # remote_dvc = "C:\\Users\\erict\\OneDrive\\Desktop\\Develop\\test_python_remote\\"

    # datasetHan = DatasetHandler(local_repo_path=local_repo_path,
    #                             bibucket_username=bit_user,
    #                             bitbucket_password=bit_psw,
    #                             bitbucket_repository_name=bit_repo_name,
    #                             bitbucket_workspace_name=bit_workspace_name,
    #                             dvc_remote_path=remote_dvc,
    #                             create_repository=False)

    # #datasetHan.copyFoldersFromTemplateRepo("classification")
    # datasetHan.initDataset()
    # datasetHan.updateTag("v1")
    # remote_dvc = "C:\\Users\\erict\\OneDrive\\Desktop\\Develop\\test_python_remote\\"

    # dvcHandler = DvcHandler(local_repo=local_repo_path,
    #                         remote_dataset=remote_dvc)

    # dvcHandler.init_git_repo_with_dvc()
    
    print("FINISH")
