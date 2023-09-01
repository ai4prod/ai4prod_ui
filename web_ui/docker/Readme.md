# Build Base Image

Usually is hosted so no need to build.

If you want to customize the base image have a look at docker folder inside ai4prod_python repository.


# Build docker image

docker build . -t ai4prod_ui


# Create Container

- {CODE_PATH}= Path to ai4prod_ui repository
- {DATA_PATH}= Path where Dataset Experiment and DatasetRemote  folders are

```
$ docker run -it -v {CODE_PATH}/web_ui/web_app:/home/Develop/ai4prod_webui  --shm-size=8192m -v {DATA_PATH}/Dataset:/home/Develop/Dataset -v ${DATA_PATH}/Experiment:/home/Develop/Experiment --gpus all --name ai4prod_web_ui -p 4040:4040 ai4prod_ui bash
```

## Example

```
$ docker run -it --shm-size=8192m -v /media/dati/Develop/ai4prod_repo/Coding/Ai4prodGuiData/Dataset:/home/Develop/Dataset -v /media/dati/Develop/ai4prod_repo/Coding/Ai4prodGuiData/Experiment:/home/Develop/Experiment --gpus all --name ai4prod_web_ui -p 4040:4040 -p 80:80 ai4prod_ui:base bash
```

You need 3 different volumes

1) First volume is to the ai4prod_python repository. Track code changes
2) Second volume is to Dataset. Folder to save Data 
3) Third volume is for experiment tracking. This folder is shared between python and C++ in order to have a reference between python model and C++ model.


## Ports

Port 7888 is used for mlflow track ui. You can run mlflow inside container with
    
    mlflow ui --port 7888 --host 0.0.0.0

Port 5001 is used to visualize dataset annotation with Fiftyone

