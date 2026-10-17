# If manage.py is just inside one 'mini_inventory' folder:
python3 mini_inventory/manage.py collectstatic --noinput

# OR if it truly sits inside a double-nested folder but needs a relative path:
python3 ./mini_inventory/manage.py collectstatic --noinput
