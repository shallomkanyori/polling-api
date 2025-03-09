echo "Creating virtual environment..."
python3.9 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Migrating database..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput