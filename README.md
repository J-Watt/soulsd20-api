# soulsd20-api
API for the Souls D20 System

Built using  
Python version 3.11.5  
Django version 4.2

## Setup

[Install Python](https://www.python.org/downloads/) if not done already.

Create a Python Virtual Environment:  
`py -m venv venv`  

Activate the venv  
`venv\Scripts\activate.bat`  
If using git bash: `. activate`

Install Django and dependancies using:  
`pip install -r requirements.txt`

More info can be found: [How to install Django](https://docs.djangoproject.com/en/4.2/topics/install/)

## Run Migrations

From within the Django project:  
`py manage.py migrate`

## Load the intial Compendium Data
  
`py manage.py loaddata initialdata.json`

## Create an Admin Superuser
 
`py manage.py createsuperuser`  
Enter your desired username and press enter. Followed by an email address and pw.

## Run Django dev server

`py manage.py runserver`

## Dev access

You can navigate the API at http://127.0.0.1:8000/  
and the admin console is located at /admin
