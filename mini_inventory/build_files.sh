#!/bin/bash

# 1. Install packages
pip install -r requirements.txt --break-system-packages

# 2. Tell Django to output static assets directly to the root folder 
# bypassing internal paths during compilation
python3 mini_inventory/manage.py collectstatic --no-input --settings=mini_inventory.settings
