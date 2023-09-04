#!/bin/bash


# Get the container name from the command line argument
container_name="docker_ai4prod_ui_container_dev_1"

# Use `docker exec` to start an interactive shell in the container
echo "Write exit and then press Enter To Create a new image ai4prod/ai4prod:base"
docker exec -it "$container_name" /bin/bash
ssh-add -D

docker container stop "$container_name"
docker commit "$container_name" ai4prod/ai4prod_ui:base
docker start "$container_name"
