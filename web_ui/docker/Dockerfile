#This dockerFile is used to create the BaseImage for ai4prod_ui

# Build from ai4prod_python dockerfile
FROM ai4prod_python_dev_official 

RUN pip3 install flask==2.2.4 
RUN pip3 install flask_sqlalchemy==3.0.0
RUN pip3 install GitPython==3.1.32
RUN pip3 install plot plotly-express
RUN pip3 install atlassian-python-api==3.40.0
RUN pip3 install turbo_flask==0.8.4 
RUN pip3 install gevent==23.7.0

WORKDIR /home/Develop/ai4prod_ui/web_ui/web_app

#Copy is executed only if we need to create baseImage to copy the UI repository Inside the container
# First time need to copy the code inside the baseImage for ui
COPY /media/dati/Develop/ai4prod_repo/Coding/ai4prod_ui /home/Develop/ai4prod_ui

#CMD ["python","production.py"]