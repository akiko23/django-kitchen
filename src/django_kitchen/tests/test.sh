#!/bin/bash

export PG_HOST=127.0.0.1
export PG_PORT=5432
export PG_USER=test
export PG_PASSWORD=test
export PG_DBNAME=postgres
export SECRET_KEY="-ets-=68-trqe71+_#cvrdu9_)kl&ro1k%2_qjt9i854-2mu%n"

python3 manage.py test $1