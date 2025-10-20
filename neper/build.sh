#!/bin/bash

set -eux

docker buildx build -t debian-neper .
docker run -v $(pwd):/output --rm -it debian-neper ./build-neper.sh
