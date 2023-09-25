
from flask import render_template, request, jsonify, Response, make_response, session, current_app, redirect, url_for,send_file
from . import home

from app.home.utils import has_trailing_slash
from app.data.dataset import datasetHandler
import datetime
from app.home import data_instance
from app.conf.conf_handler import configurationHandler

from app.db.mlflow_shema import  Dataset, DatasetVersion, Configuration
from app.db.database_instance import db_instance
from sqlalchemy import desc

@home.route("/", methods=["GET", "POST"])
def dataset():
    global datasetHandler
    
    datasets_list = Dataset.query.all()
    configurations_list= Configuration.query.all()

    if request.method == 'POST':
        # TODO: comment for reference in docker container local path is fixed
        #local_path = request.form['local_path']
        
        conf_id = request.form.get('configuration_list')
        conf = Configuration.query.filter(Configuration.id ==conf_id).first()
        
        print(conf.task)

        local_path= configurationHandler.get_dataset_path()
        repo_name = request.form['repo_name']
        #Password and used are loaded from configuration file
        # bitbucket_user = request.form['bitbucket_user']
        # bitbucket_password = request.form['bitbucket_password']

        #REMOVE Saved inside Database Instead
        #bitbucket_user, bitbucket_password= configurationHandler.get_bitbucket_cloud_credentials()
        

        # bitbucket_workspace = request.form['bitbucket_workspace']
        # dvc_remote_ssh_user = request.form['dvc_remote_ssh_user']
        # dvc_remote_ssh_psw = request.form['dvc_remote_ssh_psw']
        # dvc_remote_ssh_ip = request.form['dvc_remote_ssh_ip']
        # dvc_remote_path = request.form['dvc_remote_path']

        tag_version = "0"
         
        if(has_trailing_slash(local_path)):
            local_path= local_path +f"/{conf.task}/"
        else:
            local_path= local_path +f"/{conf.task}/"
        

        remote_path=configurationHandler.dict_conf["dataset_remote"]+ f"/{conf.task}/{repo_name}Remote/"
        
        if conf.dvc_remote_path is None:
            conf.dvc_remote_path=local_path.split("Dataset/")[0] + remote_path
        else:
            if(has_trailing_slash(conf.dvc_remote_path)):
                conf.dvc_remote_path= conf.dvc_remote_path + remote_path
            else:
                conf.dvc_remote_path= conf.dvc_remote_path + remote_path

        
        print(f"REMOTE PATH {conf.dvc_remote_path}")
        
        #-----
        # REPOSITORY SETUP
        #-----
        datasetHandler.setup(local_repo_path=local_path,
                             dvc_remote_path=conf.dvc_remote_path,
                             bibucket_username=conf.bitbucket_username,
                             bitbucket_password=conf.bitbucket_password,
                             bitbucket_repository_name=repo_name,
                             bitbucket_workspace_name=conf.bitbucket_workspace)

        datasetHandler.initDataset()
        git_remote_path = datasetHandler.gitHandler.remote_repo_url

       
        new_dataset = Dataset(init=True,
                              current_version=tag_version,
                              repo_name=repo_name,
                              local_path=local_path,
                              git_remote_path=git_remote_path,
                              bitbucket_user=conf.bitbucket_username,
                              bitbucket_password=conf.bitbucket_password,
                              bitbucket_workspace=conf.bitbucket_workspace,
                              dvc_remote_ssh_user=conf.dvc_remote_ssh_user,
                              dvc_remote_ssh_psw=conf.dvc_remote_ssh_psw,
                              dvc_remote_ssh_ip=conf.dvc_remote_ssh_ip,
                              dvc_remote_path=conf.dvc_remote_path)
        db_instance.db.session.add(new_dataset)
        db_instance.db.session.commit()
        
        #save Cfg to .yaml file
        configurationHandler.save_dataset_cfg(dataset_path=local_path,
                                              dataset_id=new_dataset.id,
                                              dataset_version_tag=tag_version,
                                              experiment_name=repo_name)

        # new Dataset will inited always with version 0
        datasetHandler.updateTag(tag_version=tag_version)
        # Init Dataset version into DB

        init_dataset_version = DatasetVersion(tag_version=tag_version,
                                              timestamp=datetime.datetime.now().timestamp(),
                                              dataset_id=new_dataset.id)

        db_instance.db.session.add(init_dataset_version)
        db_instance.db.session.commit()
        
        return redirect(url_for('home.dataset', datasets_list=datasets_list,configurations_list=configurations_list))
        
        

    #Update or Create configuration into DB

    # if conf:
    #     print("UPDATE CONF")
    #     conf.base_path_experiment= configurationHandler.dict_conf["base_path_experiment"]
    #     conf.task= configurationHandler.dict_conf["task"]
    # else:
    #     print("CREATE CONF")
    #     conf= Configuration(base_path_experiment=configurationHandler.dict_conf["base_path_experiment"],
    #                         task=configurationHandler.dict_conf["task"] )
    #     db_instance.db.session.add(conf)    
    
    # db_instance.db.session.commit()

    print(configurations_list)

    return render_template("page/home/dataset.html", datasets_list=datasets_list,configurations_list=configurations_list)


@home.route("/change_main_dataset/<int:dataset_id>/")
def change_main_dataset(dataset_id):

    print("CHANGE_DATASET_VERSION")
    print(dataset_id)
    
    dataset_instance = Dataset.query.filter_by(id=dataset_id).first()

    configuration= Configuration.query.filter_by(data_instance.conf_id == Configuration.id).first()
    # Use the select method to select this dataset
    dataset_instance.select()
    
    configurationHandler.update_gui_cfg_task(task=configuration.task,
                                             dataset_id=data_instance.id,
                                             dataset_version_tag=dataset_instance.current_version
                                             )

    return redirect(url_for('home.dataset'))

@home.route("/dataset_statistics/<int:dataset_id>", methods=['GET', 'POST'])
def dataset_statistics(dataset_id):

    # retrive data for selected dataset

    dataset_version_query = DatasetVersion.query.filter(DatasetVersion.dataset_id==dataset_id).all()

    print(dataset_version_query)

    for dataset_version in dataset_version_query:

        dt_object = datetime.datetime.fromtimestamp(
            int(float(dataset_version.timestamp)))
        formatted_date = dt_object.strftime('%d-%m-%Y')

        dataset_version.timestamp = formatted_date
        print(dataset_version.timestamp)

    dataset_query = Dataset.query.filter(Dataset.id == dataset_id).first()
    datasetHandler.setup(local_repo_path=dataset_query.local_path,
                         dvc_remote_path=dataset_query.dvc_remote_path,
                         bibucket_username=dataset_query.bitbucket_user,
                         bitbucket_password=dataset_query.bitbucket_password,
                         bitbucket_repository_name=dataset_query.repo_name,
                         bitbucket_workspace_name=dataset_query.bitbucket_workspace,
                         create_repository=False)
    data_instance.current_dataset_id = dataset_id
    data_instance.repo_name= dataset_query.repo_name

    return render_template("page/home/dataset_statistics.html", datasets_versions_list=dataset_version_query, dataset_id=dataset_id, current_version=dataset_query.current_version)


@home.route("/update_dataset_version/<int:dataset_id>/")
def update_dataset_version(dataset_id):

    # datasetHandler is already initialized from dataset_statistics.
    # WARNING removing datasetHandler initialization from dataset_statistics
    # route will cause failure on this

    dataset_version_query = DatasetVersion.query.order_by(
        desc(DatasetVersion.timestamp)).first()

    new_version = str(int(float(dataset_version_query.tag_version)) + 1)

    print(f"NEW VERSION {new_version}")

    # Update tag to remote
    datasetHandler.updateTag(tag_version=new_version)
    
    #Change Configuration value in .yaml file
    configurationHandler.update_dataset_version(new_version,dataset_id=dataset_id)

    
    # #Update tag into db
    init_dataset_version = DatasetVersion(tag_version=new_version,
                                          timestamp=datetime.datetime.now().timestamp(),
                                          dataset_id=dataset_version_query.id)

    db_instance.db.session.add(init_dataset_version)
    db_instance.db.session.commit()

    # Change current dataset version in Dataset Table to keep track which dataset_version i'am using
    dataset_query = Dataset.query.get(dataset_id)

    if dataset_query:
        dataset_query.current_version = new_version
        # Update selected database. This is used to keep track of which dataset i'am using to training.
        # In theory i can have multiple dataset
        dataset_query.select()
        db_instance.db.session.commit()

    return redirect(url_for('home.dataset_statistics', dataset_id=dataset_id))


@home.route("/change_dataset_version/<int:dataset_id>/<tag_version>/")
def change_dataset_version(dataset_id, tag_version):

    print("CHANGE_DATASET_VERSION")
    print(dataset_id)
    print(tag_version)

    # change dataset version from DVC
    datasetHandler.change_dataset_version(tag_version)
    
    configurationHandler.update_dataset_version(tag_version,
                                                dataset_id=dataset_id)

    # change dataset version to db
    dataset_query = Dataset.query.get(dataset_id)
    if dataset_query:
        dataset_query.current_version = tag_version
        # Update selected database. This is used to keep track of which dataset i'am using to training.
        # In theory i can have multiple dataset
        dataset_query.select()
        db_instance.db.session.commit()

    return redirect(url_for('home.dataset_statistics', dataset_id=dataset_id))
