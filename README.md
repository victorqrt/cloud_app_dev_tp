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
    - bash, tar, make
    - In order to build the db, you will need the mongoimport and mysql (both client only are enough) cli tools.

- To prepare the execution environment and its dependencies, simply run `make`.

Usage
-----

The first thing to do is to build the db on the remote cluster. This is automated and can be done by running `./run setup-db`.
If at any point, the data db seems broken or incomplete (e.g. previous command was interrupted), use `./run clean-db` to wipe
all databases on the cluster. You will then need to run the setup again.

Once this succeeds, you can start the webapp by using `./run webapp`. It can be accessed on port 8080 of your machine.
