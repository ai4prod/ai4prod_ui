from flask import Blueprint
from app.data.data import Data


data_instance= Data()

print(f"app_name {__name__}")
home = Blueprint("home", __name__)


from . import views
