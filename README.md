cloud_app_dev_tp
================

ESILV 5A Databases and cloud app development TP
-----------------------------------------------

This repo contains the cloud app development TP for Victor Querette and Matthieu Lanvert.
Our chosen dataset is https://relational.fit.cvut.cz/dataset/BasketballWomen.

Installation
------------

- Prerequisites:

    - python (pip, virtualenv)
    - bash
    - make

- To prepare the execution environment and its dependencies, simply run `make` in the app subfolder of the repo.

- You will then need to fetch the sql dumps from the database we chose. Running `./scripts/get_tables.sh` will get those as CSV files, one per table.

- `./scripts/import_to_cluster.sh` will push the tables to a mongoDB "import" collection on the dedicated mongo atlas cluster.

Usage
-----

Once the steps above performed, go into the `app` folder and `./run` to start the webapp :)
