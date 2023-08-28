from flask import render_template, request, jsonify, Response, make_response, session, current_app, redirect, url_for,send_file
from zipfile import ZipFile
import flask
from . import home
import os

from app.conf.conf_handler import configurationHandler
from app.db.database_instance import db_instance

from app.db.mlflow_shema import Param, Run, Metric, Dataset, DatasetVersion, Configuration
from .ai4prod_python.classification.onnxConversion import convert_to_onnx_with_hydra
import threading
import json


@home.route("/check_conversion/")
def check_conversion():

    dataset_version = request.args.get('dataset_version')
    model_path=request.args.get('model_path')


    onnx_json_data = request.args.get('data')

    print("CHECK_CONVERSION")
    print(model_path)

    model_path="C:\\Users\\erict\\OneDrive\\Desktop\\Develop\\ai4prodGuiData\\Experiment\\classification\\test_intel\\exp_6\\train\\trained_models\\"
    base_path = model_path.split("train\\", 1)[0]
    test_configuration_path=base_path + f"test\\dataset_version_{dataset_version}"

    configuration=False
    print(test_configuration_path)

    if os.path.exists(test_configuration_path) and os.path.isdir(test_configuration_path):
       configuration=True
    else:
        configuration=False

    #return jsonify({"configuration":{"value":configuration,"path":test_configuration_path}})
    print(configuration)
    if(configuration):
        return jsonify({'message': configuration,"model_path":test_configuration_path})
    return jsonify({'message': configuration})
    
    
@home.route('/deploy/<int:experiment_number>/<int:dataset_id>')
def deploy(experiment_number,dataset_id):
    
    
    print(experiment_number)
    
    configuration = db_instance.db.session.query(Configuration).first()
    dataset= db_instance.db.session.query(Dataset).filter(Dataset.id==dataset_id).first()
    
    print(configuration.base_path_experiment)
    print(configuration.task)
    print(dataset.repo_name)

    model_path=f"{configuration.base_path_experiment}{configuration.task}/{dataset.repo_name}/exp_{experiment_number}/train/trained_models/resnet18.ckpt"

    print(f"MODEL PATH {model_path}")
    
    #Cambio la configurazione di onnx
    configurationHandler.update_onnx_conversion_parameters(model_path=model_path)

    #Creo il modello Onnx

    my_thread = threading.Thread(target=convert_to_onnx_with_hydra)
    my_thread.start()

    #model_path="C:\\Users\\erict\\OneDrive\\Desktop\\Develop\\ai4prodGuiData\\Experiment\\classification\\test_intel\\exp_6\\train\\trained_models\\"
    base_path = model_path.split("train/", 1)[0]
    onnx_cfg_path=base_path + f"test\\dataset_version_{dataset.current_version}"

    onnx_json_data = json.dumps({"onnx_cfg": onnx_cfg_path})  # Convert JSON to string
    
    
    return render_template('page/home/deploy.html',model_path=model_path,dataset_version=dataset.current_version,onnx_json_data=onnx_json_data)
