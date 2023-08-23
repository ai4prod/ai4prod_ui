from flask import render_template, request, jsonify, Response, make_response, session, current_app, redirect, url_for
import flask
from . import home
from pathlib import Path
import yaml
import os
import sys
import csv
import base64
from .ai4prod_python.classification.train import train_with_hydra
import threading
import random
import plotly
import plotly.express as px
import json

from app.db.mlflow_shema import Param, Run, Metric, Dataset, DatasetVersion, Configuration
from app.db.database_instance import db_instance
from sqlalchemy import desc
import datetime
from app.data.dataset import DatasetHandler, datasetHandler
import datetime
from app.home import data_instance
from app.conf.conf_handler import configurationHandler
# Dove sono arrivato
"""
Ho creato la pagina di visualizzazione delle statistiche in una tabella. Il primo problema è che le metriche visualizzate,
si riferiscono sempre all'ultima epoca quindi è difficile eseguire un confronto tra i modelli per capire quale modello performa meglio.
(magari ultima epoca non è la migliore)

Si potrebbe creare una tabella dinamica in cui l'utente seleziona la metrica con cui eseguire i confronti dei modelli e in base alla 
stessa versione del dataset o altro che posso specificare vedere quale modello è il migliore.

Adesso da interfaccia grafica è possibile eseguire il training e i dati sono aggiornati a database che possono essere visualizzati nella
pagina

Durante il training non ho nessun tipo di feedback
Per ogni nome di esperimento è creato un database apposito. In base al valore experiment_name: testWindows nella gui_cfg.yaml
Forse dovrei creare una lista di esperimenti e quando uno clicca l'esperimento si setta il training


"""


@home.route("/", methods=["GET", "POST"])
def dataset():
    global datasetHandler
    
    conf = Configuration.query.filter_by(id=1).first()
    
    datasets_list = Dataset.query.all()

    if request.method == 'POST':
        local_path = request.form['local_path']
        repo_name = request.form['repo_name']
        bitbucket_user = request.form['bitbucket_user']
        bitbucket_password = request.form['bitbucket_password']
        bitbucket_workspace = request.form['bitbucket_workspace']
        dvc_remote_ssh_user = request.form['dvc_remote_ssh_user']
        dvc_remote_ssh_psw = request.form['dvc_remote_ssh_psw']
        dvc_remote_ssh_ip = request.form['dvc_remote_ssh_ip']
        dvc_remote_path = request.form['dvc_remote_path']

        tag_version = "0"
        
        
        
        #-----
        # REPOSITORY SETUP
        #-----
        datasetHandler.setup(local_repo_path=local_path,
                             dvc_remote_path=dvc_remote_path,
                             bibucket_username=bitbucket_user,
                             bitbucket_password=bitbucket_password,
                             bitbucket_repository_name=repo_name,
                             bitbucket_workspace_name=bitbucket_workspace)

        datasetHandler.initDataset()
        git_remote_path = datasetHandler.gitHandler.remote_repo_url

       
        new_dataset = Dataset(init=True,
                              current_version=tag_version,
                              repo_name=repo_name,
                              local_path=local_path,
                              git_remote_path=git_remote_path,
                              bitbucket_user=bitbucket_user,
                              bitbucket_password=bitbucket_password,
                              bitbucket_workspace=bitbucket_workspace,
                              dvc_remote_ssh_user=dvc_remote_ssh_user,
                              dvc_remote_ssh_psw=dvc_remote_ssh_psw,
                              dvc_remote_ssh_ip=dvc_remote_ssh_ip,
                              dvc_remote_path=dvc_remote_path)
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
        
        return redirect(url_for('home.dataset', datasets_list=datasets_list))
        
        

    #Update or Create configuration into DB

    if conf:
        print("UPDATE CONF")
        conf.base_path_experiment= configurationHandler.dict_conf["base_path_experiment"]
        conf.task= configurationHandler.dict_conf["task"]
    else:
        print("CREATE CONF")
        conf= Configuration(base_path_experiment=configurationHandler.dict_conf["base_path_experiment"],
                            task=configurationHandler.dict_conf["task"] )
        db_instance.db.session.add(conf)    
    
    db_instance.db.session.commit()

    return render_template("page/home/dataset.html", datasets_list=datasets_list)


@home.route("/dataset_statistics/<int:dataset_id>", methods=['GET', 'POST'])
def dataset_statistics(dataset_id):

    # retrive data for selected dataset

    dataset_version_query = DatasetVersion.query.all()

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



@home.route("/start_training", methods=['GET', 'POST'])
def start_training():
    
    #Before start training i need to update the experiment number
    configurationHandler.update_experiment_number_omega_conf()
    
    my_thread = threading.Thread(target=train_with_hydra)
    my_thread.start()
    result="Training Started"
    return jsonify({"result": result})

@home.route("/training/", methods=['GET', 'POST'])
def training():

    if request.method == 'POST':
        pass
        
        # uploaded_file = request.files['file']

        # print(uploaded_file)

        # if uploaded_file.filename != '':
        #     data = yaml.safe_load(uploaded_file)
        #     # Process the YAML data here (e.g., print it)
        #     print(data)

        # return render_template("page/home/training.html",filename=uploaded_file.filename)

    # datas = db_instance.db.session.query(Metric).all()

    # for data in datas:

    #     print(data.run_uuid)

    # df= px.data.medals_wide()
    # fig1= px.bar(df,x="nation",y=["gold","silver","bronze"],title="Wide=FromInput")
    # graphJson=json.dumps(fig1,cls= plotly.utils.PlotlyJSONEncoder)
    
    #Retrieve dataset statistics
    
    dataset_conf = Dataset.query.filter(Dataset.is_selected==1).all()
    
    return render_template("page/home/training.html",dataset_conf=dataset_conf,dataset_id=dataset_conf[0].id)

def move_specific_keys_to_first(dictionary, keys_to_move):
    moved_items = [(key, dictionary[key]) for key in keys_to_move if key in dictionary]
    remaining_items = [(key, value) for key, value in dictionary.items() if key not in keys_to_move]
    
    new_dict = dict(moved_items + remaining_items)
    
    return new_dict
    
@home.route("/training_metrics/<int:dataset_id>")
def training_metrics(dataset_id):

    runs_uuid_query = db_instance.db.session.query(Run).with_entities(
        Run.run_uuid).filter(Run.status == "FINISHED").all()

    run_uuids = [list(id)[0] for id in runs_uuid_query]

    print(f"Run id {run_uuids}")
    list_experiments_dict = []
    for run_uuid in run_uuids:

        tmp_dict = {}

        # TRANING METRICS
        # get last step of training
        metrics = db_instance.db.session.query(Metric).filter(
            Metric.run_uuid == run_uuid).order_by(desc(Metric.step)).first()
        # get metrics of last step of training
        metrics = db_instance.db.session.query(Metric).filter(
            Metric.run_uuid == run_uuid, Metric.step == metrics.step).all()

        for metric in metrics:
            tmp_dict["run_uuid"] = metric.run_uuid
            if(not "step" in metric.key):
                tmp_dict[metric.key] = metric.value

        # PARAMS
        runs_params_query = db_instance.db.session.query(
            Param).filter(Param.run_uuid == run_uuid).all()
        for param in runs_params_query:
            
            tmp_dict[param.key] = param.value
            
            
            

        #check if the training belongs to current dataset_id
        if(tmp_dict["dataset_id"]==str(dataset_id)):
            
            keys_to_move = ['experiment_number', 'dataset_version']
            tmp_dict = move_specific_keys_to_first(tmp_dict,keys_to_move)
            print(tmp_dict)   
            list_experiments_dict.append(tmp_dict)

    # print("query_lens")
    # print(len(runs_params_query))

    # for run_params_query in runs_params_query:
    #     tmp_dict={}
    #     tmp_dict[run_params_query.key]= run_params_query.value
    #     tmp_dict["run_id"]=run_params_query.run_uuid
    #     runs_params_dict.append(tmp_dict)

    # print(runs_params_dict)
    # for data in datas:

    #     print(data.run_uuid)

    return render_template("page/home/training_metrics.html", list_experiments_dict=list_experiments_dict)


@home.route('/optimization')
def optimization():
    return render_template('page/home/optimization.html')


@home.route('/deploy')
def deploy():
    return render_template('page/home/deploy.html')


@home.route('/configuration', methods=["GET", "POST"])
def configuration():
    if request.method == "POST":
        task = request.form.get('task')
        base_path_experiment = request.form['base_path_experiment']

        conf = Configuration(base_path_experiment=base_path_experiment,
                             task=task)
        
        db_instance.db.session.add(conf)
        db_instance.db.session.commit()
    
    return render_template('page/home/configuration.html')
