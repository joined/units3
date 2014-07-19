#!/usr/bin/env bash

# Create a virtualenv in .env dir, using python3
virtualenv -p $(which python3) .env

# Install the requirements inside the virtualenv
.env/bin/pip install -r requirements.txt