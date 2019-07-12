#!/bin/bash
#
# Script to remove docker redis container and image.
#

REDIS_CONTAINER_NAME="ls_redis"

docker container stop $REDIS_CONTAINER_NAME
docker container rm $REDIS_CONTAINER_NAME

