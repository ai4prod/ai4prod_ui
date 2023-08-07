from flask_sqlalchemy import SQLAlchemy


class Database():
    def __init__(self):
        """
        db instance of sql alchemy database
        """
        self.db=SQLAlchemy()
        print("DATABASE INSTANCE")

db_instance= Database()