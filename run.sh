#!/bin/sh
set -a
. ./.env
set +a

python -m venv virtualenv
source virtualenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

python app.py