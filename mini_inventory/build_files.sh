
# 1. Install requirements with the break-system-packages flag to bypass PEP 668
pip install -r requirements.txt --break-system-packages

# 2. Navigate into the main repository directory where manage.py is actually located
cd mini_inventory

# 3. Verify files match and run collectstatic
python3 manage.py collectstatic --no-input
