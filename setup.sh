#!/usr/bin/env bash
virtualenv -p $(which python3) .env
.env/bin/pip install -r requirements.txt