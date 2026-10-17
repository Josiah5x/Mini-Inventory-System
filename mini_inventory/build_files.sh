#!/bin/bash
# Install dependencies
pip install num2words

python3 -m pip install -r requirements.txt

# Run migrations (optional but recommended)
python3 manage.py migrate --noinput

# Collect static files
python3 manage.py collectstatic --noinput --clear