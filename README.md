# Polling App API

## Overview
This project is a RESTful API for creating and managing online polls. Users can create polls, vote on options, and retrieve real-time results. The backend is built with Django and Django Rest Framework, using PostgreSQL as the database and Swagger for API documentation.

## Technologies Used
- **Django**: Web framework for backend development.
- **Django Rest Framework (DRF)**: API framework for Django.
- **PostgreSQL**: Relational database for storing polls and votes.
- **Swagger (drf-yasg)**: API documentation.

## Installation & Setup

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- PostgreSQL
- Virtualenv (optional but recommended)

### Step 1: Clone the Repository
```sh
git clone https://github.com/shallomkanyori/polling-api.git
cd polling-api
```

### Step 2: Create a Virtual Environment & Install Dependencies
```sh
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Create a `.env` file in the project root and add the following:
```env
DEBUG=True
DJANGO_SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
```

### Step 4: Set Up the Database
Ensure PostgreSQL is running, then run:
```sh
python manage.py migrate
python manage.py createsuperuser  # Follow the prompts to create an admin user
```

### Step 5: Run the Server
```sh
python manage.py runserver
```
The API will be available at `http://127.0.0.1:8000/`.

### Step 6: Access API Documentation
Once the server is running, visit:
```
http://127.0.0.1:8000/api/docs/
```
This will display the Swagger documentation for all available endpoints.

## Running Tests
Run the following command to execute tests:
```sh
python manage.py test
```

## Deployment (Optional)
To deploy the application, use services like Heroku, Render, or Railway. Update the `.env` file with production database credentials and configure allowed hosts in `settings.py`.

## Contributing
Feel free to fork this repository and submit pull requests. Ensure that all changes are properly tested before submission.

## License
This project is open-source and available under the MIT License.