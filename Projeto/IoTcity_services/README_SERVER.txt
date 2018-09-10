The server runs on a python virtual environment.
To run the environment, on Linux you run from this file (IoTcity_services): 

1) Activate the virtual environment, with $ source bin/activate
2) Install the requirements in requirements.txt
3) Activate the rabbit MQ server, with $ sudo service rabbitmq-server restart

Then, go to IoTcity_services/server, and:
4) Start a celery worker, with $ celery -A server worker --beat -l info
5) To finally run the server, $ python manage.py runserver


CAREFUL: DO NOT PUT THE VIRTUAL ENVIRONMENT IN A PATH WITH SPACES!


Django admin:
superuser: admin
email: admin@admin.com
password:rootroot


Postgresql:
Database: db
User: admin
Password:rootroot


Diogo Ferreira,
3 March, 2017
