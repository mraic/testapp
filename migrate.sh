#!/bin/bash
docker container exec -it app_core_development bash -c "flask db migrate -m $1"
