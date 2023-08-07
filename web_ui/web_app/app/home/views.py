from flask import render_template, request, jsonify, Response, make_response, session, current_app
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

from app.db.mlflow_shema import Param,Run,Metric,Dataset,DatasetVersion
from app.db.database_instance import db_instance
from sqlalchemy import desc
import datetime
from app.data.datastet import DatasetHandler

#Dove sono arrivato
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


@home.route("/",methods=["GET","POST"])
def dataset():
    
    if request.method == 'POST':
        local_path = request.form['local_path']
        repo_name = request.form['repo_name']
        bitbucket_user = request.form['bitbucket_user']
        bitbucket_password = request.form['bitbucket_password']
        bitbucket_workspace= request.form['bitbucket_workspace']
        dvc_remote_ssh_user = request.form['dvc_remote_ssh_user']
        dvc_remote_ssh_psw = request.form['dvc_remote_ssh_psw']
        dvc_remote_ssh_ip = request.form['dvc_remote_ssh_ip']
        dvc_remote_path = request.form['dvc_remote_path']
        

        
        datasetHan= DatasetHandler(local_repo_path=local_path,
                               bibucket_username=bitbucket_user,
                               bitbucket_password=bitbucket_password,
                               bitbucket_repository_name=repo_name,
                               bitbucket_workspace_name=bitbucket_workspace)
        
        datasetHan.initDataset()
        git_remote_path= datasetHan.gitHandler.remote_repo_url
        
        new_dataset = Dataset(init=True,
                                local_path=local_path,
                                git_remote_path=git_remote_path,
                                bitbucket_user=bitbucket_user,
                                bibucket_password=bitbucket_password,
                                bitbucket_workspace= bitbucket_workspace,
                                dvc_remote_ssh_user=dvc_remote_ssh_user,
                                dvc_remote_ssh_psw=dvc_remote_ssh_psw,
                                dvc_remote_ssh_ip=dvc_remote_ssh_ip,
                                dvc_remote_path= dvc_remote_path )
        db_instance.db.session.add(new_dataset)
        db_instance.db.session.commit()

        # new_dataset_tag= DatasetVersion(version="v1",
        #                                 timestamp=datetime.datetime.now().timestamp(),
        #                                 dataset_id=new_dataset.id,
        #                                 )
        
        # db_instance.db.session.add(new_dataset_tag)
        # db_instance.db.session.commit()

    
    datasets_list= Dataset.query.all()


    return render_template("page/home/dataset.html", datasets_list=datasets_list)


@home.route("/dataset_statistics/<int:dataset_id>",methods=['GET','POST'])
def dataset_statistics(dataset_id):

    print(f"datasetID {dataset_id}")
    
    return render_template("page/home/dataset_statistics.html")

@home.route("/training", methods=['GET', 'POST'])
def training():

    if request.method == 'POST':
        
        my_thread = threading.Thread(target=train_with_hydra)
        my_thread.start()
        # uploaded_file = request.files['file']
        
        # print(uploaded_file)

        # if uploaded_file.filename != '':
        #     data = yaml.safe_load(uploaded_file)
        #     # Process the YAML data here (e.g., print it)
        #     print(data)

            #return render_template("page/home/training.html",filename=uploaded_file.filename)

    # datas = db_instance.db.session.query(Metric).all()

    # for data in datas:

    #     print(data.run_uuid)
   
    



    # df= px.data.medals_wide()
    # fig1= px.bar(df,x="nation",y=["gold","silver","bronze"],title="Wide=FromInput")
    # graphJson=json.dumps(fig1,cls= plotly.utils.PlotlyJSONEncoder)
    return render_template("page/home/training.html")

@home.route("/training_metrics")
def training_metrics():


    runs_uuid_query= db_instance.db.session.query(Run).with_entities(Run.run_uuid).filter(Run.status=="FINISHED").all()
    
    
    run_uuids = [list(id)[0] for id in runs_uuid_query]
    
    print(f"Run id {run_uuids}")
    list_experiments_dict=[]
    for run_uuid in run_uuids:
        
        tmp_dict={}
        
        #TRANING METRICS
        #get last step of training
        metrics = db_instance.db.session.query(Metric).filter(Metric.run_uuid==run_uuid).order_by(desc(Metric.step)).first()
        #get metrics of last step of training
        metrics= db_instance.db.session.query(Metric).filter(Metric.run_uuid==run_uuid,Metric.step==metrics.step).all()
        
        for metric in metrics:
            tmp_dict["run_uuid"]= metric.run_uuid
            if(not "step" in metric.key):
                tmp_dict[metric.key]=metric.value

        #PARAMS 
        runs_params_query = db_instance.db.session.query(Param).filter(Param.run_uuid==run_uuid).all()
        for param in runs_params_query:
            
            tmp_dict[param.key]=param.value
        

        

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
    
    return render_template("page/home/training_metrics.html",list_experiments_dict=list_experiments_dict)

@home.route('/optimization')
def optimization():
    return render_template('page/home/optimization.html')

@home.route('/deploy')
def deploy():
    return render_template('page/home/deploy.html')

@home.route('/configuration')
def configuration():
    return render_template('page/home/configuration.html')


