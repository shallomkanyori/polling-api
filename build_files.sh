echo "Installing requirements..."
python3.9 -m pip install -r requirements.txt

echo "Migrating database..."
python3.9 manage.py migrate --noinput

echo "Collecting static files..."
python3.9 manage.py collectstatic --noinput