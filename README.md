cloud_app_dev_tp
================

ESILV 5A Databases and cloud app development TP
-----------------------------------------------

This repo contains the cloud app development TP for Victor Querette and Matthieu Lanvert.
Our chosen dataset is https://relational.fit.cvut.cz/dataset/BasketballWomen.

`./scripts/get_tables.sh` will dump this DB into CSV files.
`./scripts/import_to_cluster.sh` will push the tables to a mongoDB "import" collection on the cluster.
