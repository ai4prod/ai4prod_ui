import threading
from .turbo_wrapper import turboWrapper
from app import app_instance
import time
from flask import render_template
import random

from app.home import data_instance
import plotly.graph_objects as go
import json
import plotly

def update_load():
    index=0
    with app_instance.app_context():
        while True:
            index= index +1
            data_instance.loss[index] = random.random()
            
            time.sleep(100)
            turboWrapper.turbo.push(turboWrapper.turbo.replace(render_template('page/turbo_component/epoch_counter.html'), 'epoch_counter'))
            turboWrapper.turbo.push(turboWrapper.turbo.replace(render_template('page/turbo_component/loss_chart.html'), 'chart1'))
            
            

#This will start the thread before app loding to firt user
@app_instance.before_first_request
def before_first_request():
    threading.Thread(target=update_load).start()


@app_instance.context_processor
def inject_load():
    #print("load inject")
    print(data_instance.epoch_counter)
    
    load = [int(random.random() * 100) / 100 for _ in range(3)]

    epoch= list(data_instance.loss.keys())
    loss_value= list(data_instance.loss.values())

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=epoch, y=loss_value, mode='lines+markers'))

    fig.update_layout(title='Line Chart with Dictionary Data',
                  xaxis_title='Date',
                  yaxis_title='Values')
    
    loss_train=json.dumps(fig,cls= plotly.utils.PlotlyJSONEncoder)


    return {'load1': load[0], 'load5': load[1], 'load15': load[2],"loss_train":loss_train}