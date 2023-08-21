from flask import Flask, render_template
import os
import sys
from app.home import home as home_blueprint
from turbo_flask import Turbo
from app.turbo_wrapper.turbo_wrapper import turboWrapper
from app.db.database_instance import db_instance

app_instance= None

def init_extensions(app: Flask):
    
    # use .init_app() on your extensions to register them on
    # the Flask instance
    turboWrapper.turbo= Turbo(app)
    


def get_root_dir_abs_path() -> str:
    """
    Get the absolute path to the root directory of the application.
    """
    # Check if the application runs in a bundled executable from PyInstaller.
    # When executed, the bundled executable get's unpacked into the temporary directory sys._MEIPASS.
    # See also: https://pyinstaller.readthedocs.io/en/stable/runtime-information.html#using-file
    return getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))

def create_app(config_object_name,db_uri) -> Flask:
    """
    :param config_object_name: The python path of the config object.
                               E.g. appname.settings.ProdConf
    :param db_uri: path to database path 
    """

    root_dir_abs_path = get_root_dir_abs_path()

    print(root_dir_abs_path)
    # Initialize the core application
    global app_instance
    
    app_instance = Flask(
        __name__,
        instance_relative_config=False,
        static_folder=os.path.join(root_dir_abs_path, "static"),
        template_folder=os.path.join(root_dir_abs_path, "templates"),
    )
    app_instance.config.from_object(config_object_name)

    print(f"Db_uri database {db_uri}")
    
    app_instance.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app_instance.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    
    db_instance.db.init_app(app_instance)

    # Initialize Plugins at startup using init_app()
    init_extensions(app_instance)

    with app_instance.app_context():
        # Register Blueprints
        app_instance.register_blueprint(home_blueprint, url_prefix="/")
        
        db_instance.db.create_all()
        
        @app_instance.errorhandler(404)
        def page_not_found(error):
            return render_template("page/errors/404.html", title="Page Not Found"), 404

        return app_instance