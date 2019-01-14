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
    - In order to build the db, you will need the mongoimport and mysql (both client only are enough) cli tools.

- To prepare the execution environment and its dependencies, simply run `make` in the app subfolder of the repo.

Usage
-----

The first thing to do is to build the db. This is automated and can be done by running `./run setup-db`.

Once this succeeds, you can start the webapp by using `./run webapp`. It can be accessed on port 8080 of your machine.
