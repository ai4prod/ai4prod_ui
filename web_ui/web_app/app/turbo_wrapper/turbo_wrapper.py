
import threading
import time
from flask import render_template

class TurboWrapper:

    def __init__(self):

        self.turbo=None

turboWrapper= TurboWrapper()




# def update_load():
#     with app_instance.app_context():
#         while True:
#             time.sleep(5)
#             turboWrapper.turbo.push(turboWrapper.turbo.replace(render_template('loadavg.html'), 'epoch_counter'))

# #This will start the thread before app loding to firt user
# @app_instance.before_first_request
# def before_first_request():
#     threading.Thread(target=update_load).start()
