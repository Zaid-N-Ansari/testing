## Installation
- git clone https://github.com/Zaid-N-Ansari/testing.git
- cd testing
- Create and Activate virtual envisronment of choice
- Install the requirements to run the Django Web App on your local machine:
- pip install -r requirements.txt

- Migrate the database to the default database that Django provides by default
- python manage.py makemigrations
- python manage.py migrate

- After you migrated the DB now, create a superuser for overseeing the system management
- python manage.py createsuperuser
- Enter the various details and
- Run the following command to start the developement server.
- python manage.py runserver
- Goto 127.0.0.1:8000 on your browser of choice.
