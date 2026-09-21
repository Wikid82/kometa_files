#!/bin/bash

set -a
source "$(dirname "$0")/.env"
set +a

docker run --name kometa_run  --rm -it -v "${KOMETA_CONFIG_DIR}:/config:rw" -e ${TZ} ${IMAGE} --collections-only  --run
