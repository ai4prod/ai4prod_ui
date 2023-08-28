from flask import render_template, request, jsonify, Response, make_response, session, current_app, redirect, url_for,send_file
from zipfile import ZipFile
import os


from . import home

from app.db.mlflow_shema import  Configuration
from app.db.database_instance import db_instance


#Views Import
import app.home.views_dataset 
import app.home.views_training 
import app.home.views_optimization
import app.home.views_deploy

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

    model_path="C:\\Users\\erict\\OneDrive\\Desktop\\Develop\\ai4prodGuiData\\Experiment\\classification\\test_intel\\exp_6\\test\\dataset_version_2\\"
    print(model_path)
    zip_filename = 'C:\\Users\\erict\\OneDrive\\Desktop\\Develop\\ai4prodGuiData\\Experiment\\classification\\test_intel\\exp_6\\test\\dataset_version_2\\configuration.zip'

    # Create a zip file on-the-fly containing the folder's contents
    with ZipFile(zip_filename, 'w') as zipf:
        for root, dirs, files in os.walk(model_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, model_path))

    # Send the zip file as a download response
    return send_file(zip_filename, as_attachment=True)


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
