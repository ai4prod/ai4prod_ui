from flask import render_template, request, jsonify, Response, make_response, session, current_app, redirect, url_for,send_file
import zipfile
import os


from . import home

from app.db.mlflow_shema import  Configuration
from app.db.database_instance import db_instance


#Views Import
import app.home.views_dataset 
import app.home.views_training 
import app.home.views_optimization
import app.home.views_deploy

import json


from pathlib import Path 
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


@home.route('/download_folder/')
def download_folder():

    # model_path=request.args.get('model_path')
    data = request.args.get('onnx_json_data')

    print("DATA")
    print(data)
    
    excluded_extensions = ['.zip']

    configuration_path= json.loads(data)["onnx_cfg"] +"/"
     
    download_name= "download"
    download_folder= configuration_path +"download/"

    #create download folder if not exists
    Path(download_folder).mkdir(
            parents=True, exist_ok=True)

    
    onnx_model_path= json.loads(data)["model_path"] + "onnx/" 

    
    zip_path = download_folder + download_name + '.zip'
    folder_path = configuration_path

    #folder_path= "C:/Users/erict/OneDrive/Desktop/Develop/ai4prodGuiData/Experiment/classification/test_intel/exp_6/test/dataset_version_2/"

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if excluded_extensions is None or not file_path.endswith(tuple(excluded_extensions)):
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname=arcname)


    # Send the zip file as a download response
    return send_file(zip_path, as_attachment=True, download_name=f"{download_name}.zip")


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
