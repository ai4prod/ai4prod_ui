from flask import render_template, request, jsonify, Response, make_response, session, current_app, redirect, url_for,send_file
import flask
from . import home

from app.conf.conf_handler import configurationHandler
from .ai4prod_python.classification.train import train_with_hydra
import threading

from app.db.mlflow_shema import Param, Run, Metric, Dataset
from app.db.database_instance import db_instance
from sqlalchemy import desc

import plotly
import plotly.express as px

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

def move_specific_keys_to_first(dictionary, 
                                keys_to_move,
                                include_others=False):
    moved_items = [(key, dictionary[key]) for key in keys_to_move if key in dictionary]
    remaining_items=[]
    if include_others:
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
            # TODO: some keys are task specific like val_accuracy is only for classification
            # Need to change based on different task
            keys_to_move = ['experiment_number', 'dataset_version',"dataset_path","val_accuracy","val_cross_entropy","dataset_id"]
            tmp_dict = move_specific_keys_to_first(tmp_dict,keys_to_move)
            print(tmp_dict)   
            list_experiments_dict.append(tmp_dict)
            

    return render_template("page/home/training_metrics.html", list_experiments_dict=list_experiments_dict)

