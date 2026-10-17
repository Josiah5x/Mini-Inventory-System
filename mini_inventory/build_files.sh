#!/bin/bash

# 1. Install corrected requirements configuration
pip install -r requirements.txt --break-system-packages

# 2. Check if the mini_inventory folder exists, and step inside if it does
if [ -d "mini_inventory" ]; then
    cd mini_inventory
fi

# 3. Collect static files safely (Since you did 'cd mini_inventory', manage.py is right here)
python3 manage.py collectstatic --noinput
