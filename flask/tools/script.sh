#! /usr/bin/bash

cd

rm -rf PythonREST

python3 -m venv PythonREST/Flask01

source PythonREST/Flask01/bin/activate

pip install flask-restful flask-swagger-ui
pip install flask_sqlalchemy flask_bcrypt pyjwt psycopg2-binary redis flasgger

cp -r /application/app PythonREST/api

python3 PythonREST/api/api.py