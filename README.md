# README

Install Requirenments
> pip install -r requirements.txt

Activate the application environment:
> source env/bin/activate

Run the application localy:
> flask run

Backup the installed dependencies to requirenments.txt file:
> pip freeze > requirements.txt

Heroku logs:
> heroku logs -n 1500

Heroku bash:
> heroku run bash

## Windows

> python -m virtualenv venv
> venv\Scripts\activate

Run app:
> set FLASK_APP=run.py
> flask run
