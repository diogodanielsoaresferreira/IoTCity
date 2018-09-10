
The broker runs on a python virtual environment.
To run the environment, on Linux you run from this file (IoTcity_services): 

1) Activate the virtual environment, with $ source bin/activate
2) Activate the rabbit MQ server, with $ sudo service rabbitmq-server restart

Then, go to IoTcity_services/local_broker, and:
3) Start a celery worker, with $ celery -A local_broker worker -l info
4) To finally run the server, $ python manage.py runserver


CAREFUL: DO NOT PUT THE VIRTUAL ENVIRONMENT IN A PATH WITH SPACES!



*** Requirements ***
sudo apt-get install rabbitmq-server=3.5.7
pip install django==1.10
pip install requests==2.11.1
pip install djangorestframework==3.5.4
pip install markdown==2.6.8
pip install django-filter==1.0.1
pip install celery==40.2
pip install django_celery_results==1.0.1


The Broker has 4 API's:
-> Create Stream
-> Send Data
-> Read Data
-> Subscribe
-> Delete Stream

It is recommended to install a Rest Client (p.e. Advanced Rest Client Chrome Extension) to emulate the requests with POST and GET headers.

For testing purposes, you can use http://putsreq.com to create a PutsReq and specify the provided URL as point_of_contact, if needed.

All contacts need an authentication token. In the testing phase, the token is "Bearer teste".
It can be added on the Header {"Authorization": "Bearer teste"}


* Create Stream

POST /streams/name_stream/create
Header:
AUTHORIZATION: Bearer Teste


* Send data to stream

POST /streams/name_stream/send
Header:
AUTHORIZATION: Bearer Teste

Body:
{"timestamp":12,
"value":12,
"ttl":12}



* Read values on stream

POST /streams/name_stream/read
Header:
AUTHORIZATION: Bearer Teste

Body:
{"values":{
	{"timestamp":12,
	"value":12,
	"ttl":12},

	{"timestamp":24,
	"value":10,
	"ttl":5},
	...
}


* Subscribe to point of contact

POST /streams/name_stream/subscribe
Header:
AUTHORIZATION: Bearer Teste

Body:
{"point_of_contact":"http://..."}


* Delete Stream

DELETE /streams/name_stream/delete
Header:
AUTHORIZATION: Bearer Teste


Diogo Ferreira,
3 March, 2017
