from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import sys
import requests
import tasks


points_of_contact = {}
messages = {}


'''
Create Stream

POST /streams/name_stream/create
Header:
AUTHORIZATION: Bearer Teste

'''

@api_view(['POST'])
def create_stream(request, name):
	
	if request.method == 'POST':
		if 'HTTP_AUTHORIZATION' not in request.META or request.META['HTTP_AUTHORIZATION'] != "Bearer teste":
			return Response({"status":"error","description":"Not Authorized"}, status=status.HTTP_401_UNAUTHORIZED)

		messages[name] = []
		return Response({"status":"created","name":name}, status=status.HTTP_200_OK)

'''
Send data to stream

POST /streams/name_stream/send
Header:
AUTHORIZATION: Bearer Teste

Body:
{"timestamp":12,
"value":12,
"ttl":12}

'''

@api_view(['POST'])
def send_data(request, name):

	if request.method == 'POST':
		if 'HTTP_AUTHORIZATION' not in request.META or request.META['HTTP_AUTHORIZATION'] != "Bearer teste":
			return Response({"status":"error","description":"Not Authorized"}, status=status.HTTP_401_UNAUTHORIZED)

		# Parse the message body
		try:
			payload = {"ttl":request.data["ttl"],"timestamp":request.data["timestamp"],"value":request.data["value"]}
		
		except Exception as url_err:
			print(url_err)
			return Response({"status":"error","description":"Incorrect Message body"}, status=status.HTTP_400_BAD_REQUEST)

		# Saves message
		try:
			messages[name] += [payload]
		except Exception as err:
			print(err)
			return Response({"status":"error", "description":"Stream not found"}, status=status.HTTP_404_NOT_FOUND)
		

		# Broadcasts message to all the subscribers
		if name in points_of_contact:
			for url in points_of_contact[name]:
				try:
					# Assynchronous task with Rabbitmq and Celery
					tasks.send_data.delay(url, payload)
				except Exception as url_err:
					print(url_err)
		return Response({"status":"ok","name":name}, status=status.HTTP_200_OK)

'''
Read values on stream

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
	"ttl":5}
}
'''

@api_view(['GET'])
def read(request, name):

	if request.method == 'GET':
		if 'HTTP_AUTHORIZATION' not in request.META or request.META['HTTP_AUTHORIZATION'] != "Bearer teste":
			return Response({"status":"error","description":"Not Authorized"}, status=status.HTTP_401_UNAUTHORIZED)

		try:
			message = messages[name]
			messages[name] = []
		except Exception as err:
			print(err)
			return Response({"status":"error", "description":"Stream not found"}, status=status.HTTP_404_NOT_FOUND)
		return Response({"values":message}, status=status.HTTP_200_OK)


'''
Subscribe to point of contact

POST /streams/name_stream/subscribe
Header:
AUTHORIZATION: Bearer Teste

Body:
{"point_of_contact":"http://..."}
'''

@api_view(['POST'])
def subscribe(request, name):

	if request.method == 'POST':
		if 'HTTP_AUTHORIZATION' not in request.META or request.META['HTTP_AUTHORIZATION'] != "Bearer teste":
			return Response({"status":"error","description":"Not Authorized"}, status=status.HTTP_401_UNAUTHORIZED)

		if name not in messages:
			return Response({"status":"error", "description":"Stream not found"}, status=status.HTTP_404_NOT_FOUND)

		try:
			pc = request.data["point_of_contact"]
			if pc!="" and (name not in points_of_contact or pc not in points_of_contact[name]):
				if name not in points_of_contact:
					points_of_contact[name] = [pc]
				else:
					points_of_contact[name] += [pc]
			return Response({"status":"subscribed","name":name}, status=status.HTTP_200_OK)
		except Exception as err:
			print(err)
			return Response({"status":"error", "description":"Incorrect Message body"}, status=status.HTTP_400_BAD_REQUEST)

'''
Delete Stream

DELETE /streams/name_stream/delete
Header:
AUTHORIZATION: Bearer Teste

'''

@api_view(['DELETE'])
def delete(request, name):
	
	if request.method == 'DELETE':
		if 'HTTP_AUTHORIZATION' not in request.META or request.META['HTTP_AUTHORIZATION'] != "Bearer teste":
			return Response({"status":"error","description":"Not Authorized"}, status=status.HTTP_401_UNAUTHORIZED)

		points_of_contact.pop(name, None)
		messages.pop(name, None)

		return Response({"status":"deleted","name":name}, status=status.HTTP_200_OK)
