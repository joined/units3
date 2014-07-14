#!/usr/bin/env bash
virtualenv -p $(which python3) --no-site-packages .env
source .env/bin/activate
pip install -r requirements.txt
deactivate
