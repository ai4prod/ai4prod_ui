from sqlalchemy import BigInteger, Boolean, Column, Enum, Float, ForeignKey, ForeignKeyConstraint, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.db.database_instance import db_instance

Base = declarative_base()
metadata = Base.metadata

#ML FLOW IMPORTED CLASS

class Experiment(Base):
    __tablename__ = 'experiments'

    experiment_id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    artifact_location = Column(String(256))
    lifecycle_stage = Column(Enum('active', 'deleted'))
    creation_time = Column(BigInteger)
    last_update_time = Column(BigInteger)


class RegisteredModel(Base):
    __tablename__ = 'registered_models'

    name = Column(String(256), primary_key=True, unique=True)
    creation_time = Column(BigInteger)
    last_updated_time = Column(BigInteger)
    description = Column(String(5000))


class ExperimentTag(Base):
    __tablename__ = 'experiment_tags'

    key = Column(String(250), primary_key=True, nullable=False)
    value = Column(String(5000))
    experiment_id = Column(ForeignKey('experiments.experiment_id'), primary_key=True, nullable=False)

    experiment = relationship('Experiment')


class ModelVersion(Base):
    __tablename__ = 'model_versions'

    name = Column(ForeignKey('registered_models.name', onupdate='CASCADE'), primary_key=True, nullable=False)
    version = Column(Integer, primary_key=True, nullable=False)
    creation_time = Column(BigInteger)
    last_updated_time = Column(BigInteger)
    description = Column(String(5000))
    user_id = Column(String(256))
    current_stage = Column(String(20))
    source = Column(String(500))
    run_id = Column(String(32))
    status = Column(String(20))
    status_message = Column(String(500))
    run_link = Column(String(500))

    registered_model = relationship('RegisteredModel')


class RegisteredModelTag(Base):
    __tablename__ = 'registered_model_tags'

    key = Column(String(250), primary_key=True, nullable=False)
    value = Column(String(5000))
    name = Column(ForeignKey('registered_models.name', onupdate='CASCADE'), primary_key=True, nullable=False)

    registered_model = relationship('RegisteredModel')


class Run(Base):
    __tablename__ = 'runs'

    run_uuid = Column(String(32), primary_key=True)
    name = Column(String(250))
    source_type = Column(Enum('NOTEBOOK', 'JOB', 'LOCAL', 'UNKNOWN', 'PROJECT'))
    source_name = Column(String(500))
    entry_point_name = Column(String(50))
    user_id = Column(String(256))
    status = Column(Enum('SCHEDULED', 'FAILED', 'FINISHED', 'RUNNING', 'KILLED'))
    start_time = Column(BigInteger)
    end_time = Column(BigInteger)
    source_version = Column(String(50))
    lifecycle_stage = Column(Enum('active', 'deleted'))
    artifact_uri = Column(String(200))
    experiment_id = Column(ForeignKey('experiments.experiment_id'))
    deleted_time = Column(BigInteger)

    experiment = relationship('Experiment')


class LatestMetric(Base):
    __tablename__ = 'latest_metrics'

    key = Column(String(250), primary_key=True, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(BigInteger)
    step = Column(BigInteger, nullable=False)
    is_nan = Column(Boolean, nullable=False)
    run_uuid = Column(ForeignKey('runs.run_uuid'), primary_key=True, nullable=False, index=True)

    run = relationship('Run')


class Metric(Base):
    __tablename__ = 'metrics'

    key = Column(String(250), primary_key=True, nullable=False)
    value = Column(Float, primary_key=True, nullable=False)
    timestamp = Column(BigInteger, primary_key=True, nullable=False)
    run_uuid = Column(ForeignKey('runs.run_uuid'), primary_key=True, nullable=False, index=True)
    step = Column(BigInteger, primary_key=True, nullable=False, server_default=text("'0'"))
    is_nan = Column(Boolean, primary_key=True, nullable=False, server_default=text("'0'"))

    run = relationship('Run')


class ModelVersionTag(Base):
    __tablename__ = 'model_version_tags'
    __table_args__ = (
        ForeignKeyConstraint(['name', 'version'], ['model_versions.name', 'model_versions.version'], onupdate='CASCADE'),
    )

    key = Column(String(250), primary_key=True, nullable=False)
    value = Column(String(5000))
    name = Column(String(256), primary_key=True, nullable=False)
    version = Column(Integer, primary_key=True, nullable=False)

    model_version = relationship('ModelVersion')


class Param(Base):
    __tablename__ = 'params'

    key = Column(String(250), primary_key=True, nullable=False)
    value = Column(String(500), nullable=False)
    run_uuid = Column(ForeignKey('runs.run_uuid'), primary_key=True, nullable=False, index=True)

    run = relationship('Run')

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Tag(Base):
    __tablename__ = 'tags'

    key = Column(String(250), primary_key=True, nullable=False)
    value = Column(String(5000))
    run_uuid = Column(ForeignKey('runs.run_uuid'), primary_key=True, nullable=False, index=True)

    run = relationship('Run')

#CUSTOM TABLE

#HANDLE DATASET_VERSIONING
class Dataset(db_instance.db.Model):
    __tablename__ = 'dataset'
    """
    :param current_version: Keep track of the version selected for training

    """
    id = Column(Integer, primary_key=True)
    init= Column(Boolean,default=False)
    is_selected = Column(Integer, nullable=False, server_default='0')
    current_version = Column(String(10))
    repo_name= Column(String(40))
    local_path = Column(String(200))
    git_remote_path = Column(String(200))
    bitbucket_user= Column(String(60))
    bitbucket_password= Column(String(60))
    bitbucket_workspace= Column(String(60))
    dvc_remote_ssh_user = Column(String(60))
    dvc_remote_ssh_psw = Column(String(60))
    dvc_remote_ssh_ip = Column(String(60))
    dvc_remote_path= Column(String(200))
    dataset_version = relationship('DatasetVersion', back_populates='dataset')

    def select(self):
        # Deselect all items
        Dataset.query.update({Dataset.is_selected: 0})

        # Select the current item
        self.is_selected = 1
        db_instance.session.commit()


class DatasetVersion(db_instance.db.Model):
    __tablename__ = 'dataset_version'

    id = Column(Integer, primary_key=True)
    tag_version = Column(String(10))
    timestamp = Column(String(20))
    dataset_id = Column(Integer, ForeignKey('dataset.id'))
    dataset = relationship('Dataset', back_populates='dataset_version')
    