# Build Base Image

Usually is hosted so no need to build.

If you want to customize the base image have a look at docker folder inside ai4prod_python repository.


# Create Container


docker run -it -v /home/etondelli/Develop/ai4prod_ui/web_ui/web_app:/home/Develop/ai4prod_web_ui  --shm-size=8192m -v /home/etondelli/Develop/guiData/Dataset:/home/Develop/Dataset -v /home/etondelli/Develop/guiData/Experiment:/home/Develop/experiment --gpus all --name ai4prod_web_ui -p 4040:4040 ai_training bash


You need 3 different volumes

1) First volume is to the ai4prod_python repository. Track code changes
2) Second volume is to Dataset. Folder to save Data 
3) Third volume is for experiment tracking. This folder is shared between python and C++ in order to have a reference between python model and C++ model.


## Ports

Port 7888 is used for mlflow track ui. You can run mlflow inside container with
    
    mlflow ui --port 7888 --host 0.0.0.0

Port 5001 is used to visualize dataset annotation with Fiftyone

