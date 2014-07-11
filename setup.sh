#!/usr/bin/env bash
virtualenv --no-site-packages .env
source .env/bin/activate
pip install -r requirements.txt
deactivate
