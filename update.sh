git pull
python3 manage.py migrate
python3 manage.py collectstatic
systemctl restart apache2
