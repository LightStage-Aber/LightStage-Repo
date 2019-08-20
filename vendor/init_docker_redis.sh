#!/bin/bash
#
# Script to build docker's redis container on default port 6379
#

REDIS_PORT=6379
REDIS_CONTAINER_NAME="ls_redis"

CurrDir=$(dirname $(realpath $0))
cd $CurrDir/redis/Simple
docker build -t $REDIS_CONTAINER_NAME .
docker run --name $REDIS_CONTAINER_NAME -d $REDIS_CONTAINER_NAME

REDIS_IP=$("docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $REDIS_CONTAINER_NAME")
nc -v $REDIS_IP $REDIS_PORT

