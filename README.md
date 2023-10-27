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
`manage.py migrate`

## Run Django dev server

`manage.py runserver`
