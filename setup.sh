#!/usr/bin/env bash
virtualenv -p $(which python3) .env
source .env/bin/activate
pip install -r requirements.txt
deactivate
