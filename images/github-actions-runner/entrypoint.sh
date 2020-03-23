#!/usr/bin/env bash
set -x
set -e
sudo chgrp docker /var/run/docker.sock
ls /run/secrets/
/register-builder.sh $@
cd /worker-root
./run.sh
