# soulsd20-api
API for the Souls D20 System

Built using  
Python version 3.11.5  
Django version 4.2

## Setup

[Install Python](https://www.python.org/downloads/) if not done already.

Navigate to the project folder in a terminal.  

Create a Python Virtual Environment:  
`py -m venv venv`  

Activate the venv  
`venv\Scripts\activate.bat`  
If using git bash, navigate into the Scripts folder and type: `. activate`  
alternativly run  
`venv\Scripts\Activate.ps1`  

Navigate to the top folder again (`cd ../..`), and install Django and dependancies using:  
`pip install -r requirements.txt`

More info can be found: [How to install Django](https://docs.djangoproject.com/en/4.2/topics/install/)

## Run Migrations

Navigate into `cd soulsd20api`.  

From within the Django project run:  
`py manage.py migrate`

## Load the Intial Compendium Data
  
`py manage.py loaddata initialdata.json`

## Create an Admin Superuser
 
`py manage.py createsuperuser`  
Enter your desired username and press enter. Followed by an email address and pw.  
if that does not work you may need to try:  `winpty python manage.py createsuperuser`

## Run Django dev server

`py manage.py runserver`

## Dev access

You can navigate the API at http://127.0.0.1:8000/  
and the admin console is located at /admin

## Shutting Down
To turn off the server enter `CTRL + C`  
To turn off the virtual environment enter `deactivate`

## Updating and Runing the server again
You can simply Activate the venv and use runserver again (after navigating to the correct folders).  

If there are updates and changes:
- Use `git pull` to grab any code updates.
- Follow "Run Migrations" instructions

If there are major changes to the DB structure you can reset by doing the following:
- First you will need to delete the file `db.sqlite3`
- Next follow all the instructions again starting from "Run Migrations" after activating the venv. 
