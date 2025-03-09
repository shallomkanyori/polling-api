#!bin/sh

echo "Installing requirements..."
pip install -r requirements.txt

echo "Migrating database..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput