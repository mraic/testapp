#!/bin/bash
docker exec -it app_core_development bash -c "flask db_dev recreate"
docker exec -it app_core_development bash -c "flask db_dev create_postgis_extension"
docker exec -it app_core_development bash -c "flask db upgrade"
docker exec -it app_core_development bash -c "flask db_migrations generate_categories"