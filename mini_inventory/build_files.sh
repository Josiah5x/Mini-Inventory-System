# 1. Create a virtual environment using the active Python 3.14 runtime
python3 -m venv venv

# 2. Activate the virtual environment
source venv/bin/activate

# 3. Install your dependencies safely inside the virtual environment
pip install -r requirements.txt

# 4. Run your Django collectstatic command using the environment's python
python3 manage.py collectstatic --noinput
