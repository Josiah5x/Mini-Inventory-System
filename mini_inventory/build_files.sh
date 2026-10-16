#!/bin/bash

# 1. Force upgrade pip and install dependencies safely
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# 2. Run Django operations
python3 mini_inventory/manage.py collectstatic --noinput --clear
python3 mini_inventory/manage.py migrate
