# Polling App API
[![Live API](https://img.shields.io/badge/API-Live-brightgreen)](https://polling-api-theta.vercel.app/)

## Overview
This project is a RESTful API for creating and managing online polls. Users can create polls, vote on options, and retrieve real-time results. The backend is built with Django and Django Rest Framework, using PostgreSQL as the database and Swagger for API documentation.

---
## Technologies Used
- **Django**: Web framework for backend development.
- **Django Rest Framework (DRF)**: API framework for Django.
- **PostgreSQL**: Relational database for storing polls and votes.
- **Swagger (drf-yasg)**: API documentation.

---
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

---
## API Usage
The API is documented using Swagger UI.  
You can explore the endpoints here:  
🔗 [Docs](https://polling-api-theta.vercel.app/api/docs/)

### Authentication
- **Signup**: `POST /api/signup/`
- **Login**: `POST /api/auth/login/`
- **Logout**: `POST /api/auth/logout/`
- **Get User Info**: `GET /api/users/{id}/`
- **Delete Account**: `DELETE /api/users/{id}/`

### Poll Management
- **Create Poll**: `POST /api/polls/`
- **List Polls**: `GET /api/polls/`
- **Retrieve Poll**: `GET /api/polls/{id}/`
- **Update Poll**: `PUT /api/polls/{id}/` (Only creator/admin)
- **Delete Poll**: `DELETE /api/polls/{id}/` (Only creator/admin)

### Voting
- **Vote on a Poll**: `POST /api/polls/{id}/vote/`

### Poll Results
- **Get Poll Results**: `GET /api/polls/{id}/results/`

### Filtering & Searching
Polls can be filtered by:
- Title: `GET /api/polls/?title=<search_term>`
- Created by: `GET /api/polls/?created_by=<user_id>`
- Ongoing Polls: `GET /api/polls/?ongoing=true`

---
## Rate Limiting
Implemented rate limits:
- **Voting**: Limited per IP/session
- **Poll Creation**: Limited per user
- **Signup**: Limited per IP

---
## Deployment (Optional)
To deploy the application, use services like Heroku, Render, or Railway. Update the `.env` file with production database credentials and configure allowed hosts in `settings.py`.

The API is deployed on **Vercel** and accessible at:
🔗 [Live API](https://polling-api-theta.vercel.app/)

---
## Future Enhancements
- WebSocket support for real-time poll updates
- Implement poll categories
- Email notifications for poll creators

---
## Contributing
Feel free to fork this repository and submit pull requests. Ensure that all changes are properly tested before submission.

---
## License
This project is open-source and available under the MIT License.