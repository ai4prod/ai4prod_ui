from flask import flash, render_template, request, jsonify, Response, make_response, session, current_app, redirect, url_for, send_file
import zipfile
import os


from . import home

from app.db.mlflow_shema import Configuration
from app.db.database_instance import db_instance


# Views Import
import app.home.views_dataset
import app.home.views_training
import app.home.views_optimization
import app.home.views_deploy

import json
from pathlib import Path


from app.home.utils import generate_ssh_configuration
from app.conf.conf_handler import configurationHandler
from sqlalchemy.exc import IntegrityError
import random
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

    configuration_path = json.loads(data)["onnx_cfg"] + "/"

    download_name = "download"
    download_folder = configuration_path + "download/"

    # create download folder if not exists
    Path(download_folder).mkdir(
        parents=True, exist_ok=True)

    onnx_model_path = json.loads(data)["model_path"] + "onnx/"

    zip_path = download_folder + download_name + '.zip'
    configuration_path

    # folder_path= "C:/Users/erict/OneDrive/Desktop/Develop/ai4prodGuiData/Experiment/classification/test_intel/exp_6/test/dataset_version_2/"

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(configuration_path):
            for file in files:
                file_path = os.path.join(root, file)
                if excluded_extensions is None or not file_path.endswith(tuple(excluded_extensions)):
                    arcname = os.path.relpath(file_path, configuration_path)
                    zipf.write(file_path, arcname=arcname)
        for root, _, files in os.walk(onnx_model_path):
            for file in files:
                file_path = os.path.join(root, file)
                if excluded_extensions is None or not file_path.endswith(tuple(excluded_extensions)):
                    arcname = os.path.relpath(file_path, onnx_model_path)
                    zipf.write(file_path, arcname=arcname)

    # Send the zip file as a download response
    return send_file(zip_path, as_attachment=True, download_name=f"{download_name}.zip")


@home.route('/configuration/generat_ssh_key/', methods=['POST'])
def get_data():
    data = request.get_json()

    email = data["email"]
    print(email)
    ssh_key = generate_ssh_configuration(email)
    ssh_key = {"ssh_key": ssh_key}
    return jsonify(ssh_key)


@home.route('/configuration', methods=["GET", "POST"])
def configuration():

   

    if request.method == "POST":
        print("Form submission")
        configuration_name = request.form['configuration_name']
        # TODO: At current time user email is not saved to database
        bitbucket_email = ""
        base_path_experiment = request.form['base_path_experiment']
        task = request.form.get('task')
        bitbucket_workspace = request.form['bitbucket_workspace']
        bitbucket_username = request.form['bitbucket_username']
        bitbucket_password = request.form['bitbucket_password']
        dvc_remote_ssh_user = request.form['dvc_remote_ssh_user']
        dvc_remote_ssh_psw = request.form['dvc_remote_ssh_psw']
        dvc_remote_ssh_ip = request.form['dvc_remote_ssh_ip']
        dvc_remote_path = request.form['dvc_remote_path']

        if (request.form['base_path_experiment'] == ""):
            base_path_experiment = configurationHandler.base_path_experiment
        
        conf = Configuration(
            configuration_name=configuration_name,
            bitbucket_email=bitbucket_email,
            base_path_experiment=base_path_experiment,
            task=task,
            bitbucket_username=bitbucket_username,
            bitbucket_password=bitbucket_password,
            bitbucket_workspace=bitbucket_workspace,
            dvc_remote_ssh_user=dvc_remote_ssh_user,
            dvc_remote_ssh_psw=dvc_remote_ssh_psw,
            dvc_remote_ssh_ip=dvc_remote_ssh_ip,
            dvc_remote_path=dvc_remote_path,
        )

        db_instance.db.session.add(conf)
        db_instance.db.session.commit()
        flash('Configurazione creata con successo', 'success')
        return redirect(url_for('home.configuration'))
        # except IntegrityError as e:
        #     print("INTEGRITY")
        #     # Rollback the transaction to prevent data corruption
        #     db_instance.db.session.rollback()
        #     flash('Nome configurazione già presente', 'error')
        #     return redirect(url_for('home.configuration'))

        # except Exception as e:
        #     error_message = "Errore generico.Riprova"

    return render_template('page/home/configuration.html')
