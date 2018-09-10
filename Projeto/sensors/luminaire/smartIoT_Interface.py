# Interface for interaction with SmartIoT
# Diogo Ferreira, March 2016

import requests
import base64
import sys
import json


def test():

	# Not Finished:
	# remove stream e device

	token = ""
	device_id = "newdevice"
	device_name = "newdevice_name"
	device_password = "newdevice_secret"
	device_description = "Device Description"

	stream_id = ""
	stream_name = "newstream_name"
	stream_password = "newstream_password"
	stream_desc = "Stream descriptions"

	subs_name = "newsubs_name"
	subs_desc = "subs description"
	subscription_id = ""
	subscriber_id = "newsubscriber id"



	# Authenticate
	token = authenticate("https://iot.alticelabs.com","ua1", "8ik8fm0h8mqer821agae3qg29ve1kl84d9b0svsiesqj52lil59g")
	print(token)
	token = token[1]
	
	# Add device
	dev = register_device("https://iot.alticelabs.com", device_id, device_password, token, device_name, device_description)
	print(dev)
	
	# Retrieve details
	det = device_details("https://iot.alticelabs.com", device_id, token)
	print(det)

	# Device authentication
	auth = device_authentication("https://iot.alticelabs.com", device_id, device_password)
	print(auth)

	# Create device stream
	create = create_stream("https://iot.alticelabs.com", token, device_id, stream_name)
	print(create)

	# List device streams
	lis = list_streams("https://iot.alticelabs.com", token, device_id)
	print(lis)
	stream_id = json.loads(lis[1])["streams"][0]["id"]

	# Create subscription
	subs = create_subscription("https://iot.alticelabs.com", token, subs_name, subs_desc, subscriber_id, device_id, stream_name, "active", 10, 3600, 5, "30,45,60")
	print(subs)
	subscription_id = json.loads(subs[1])["id"]

	# Get subscription details
	s_det = get_subscription_details("https://iot.alticelabs.com", token, subscription_id)
	print(s_det)
	
	# Publish device stream
	publ = publish_into_stream("https://iot.alticelabs.com", auth[1], device_id, stream_name, "2016-09-10T19:15:00.325Z", 100, 300)
	print(publ)
	
	# Read device stream
	read = read_stream("https://iot.alticelabs.com", token, device_id, stream_name, "2014-09-01T00:00:00.000Z", "2017-09-30T23:59:59.000Z")
	print(read)

	# Update subscription
	#s_upd = update_subscription("https://iot.alticelabs.com", token, subs_id, "My_Subscription", "Long description", "suspended", 12, 3600, 15, "30,45,60,120", None)
	#print(s_upd)

	# Retrieve subscription values
	ret = retrieve_subscription_values("https://iot.alticelabs.com", auth[1], subscription_id)
	print(ret)
	
	# Remove subscription
	s_rem = remove_subscription("https://iot.alticelabs.com", token, subscription_id)
	print(s_rem)

	# Remove device stream
	remove = remove_stream("https://iot.alticelabs.com", token, device_id, stream_name)
	print(remove)

	# Update device
	#upd = update_device("https://iot.alticelabs.com", device_id, token, "test2", "test2", "test2")
	#print(upd)
	
	# Remove device
	rem = remove_device("https://iot.alticelabs.com", device_id, token)
	print(rem)




'''
Account Authentication

parameters: url of web service, user id, user password

returns a tuple (status_code, token)

status codes:
0 Could not establish connection with url
201 Created
401 Unauthorized
500 Internal Server Error

'''

def authenticate(url, id, secret):
	encoded = base64.b64encode(id+":"+secret)
	headers = {"Authorization":"Basic " + encoded}

	try:
		r = requests.post(url+"/accounts/token", headers=headers)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0,0

	return r.status_code, r.text


'''
Device authentication

parameters: url of web service, device id, device password

returns a tuple (status_code, token)

Status codes:
201 Created
401 Unauthorized
500 Internal Server Error
'''

def device_authentication(url, id, secret):
	encoded = base64.b64encode(id+":"+secret)
	headers = {"Authorization":"Basic " + encoded, 'content-type': 'application/json'}
	
	try:
		r = requests.post(url+"/devices/token", headers=headers)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0,0

	return r.status_code, r.text


'''
Register device

parameters: url of web service, device id, device password, account access token,
device name, device description

returns a tuple (status code, json message)
status_code:
0 if could not connect to url
201 Created
400 Bad Request
401 Unauthorized
403 Forbidden
500 Internal Server Error

'''

def register_device(url, id, secret, token, name, description):
	headers = {"Authorization":"Bearer " + token, 'content-type': 'application/json'}
	body = {"id":id, "secret":secret, "name":name, "description":description}
	
	try:
		r = requests.post(url+"/devices", headers=headers, json=body)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0,0

	return r.status_code,r.text


'''
Retrieve device details

parameters: url of web service, device id, device access token
returns a tuple (status code, json device details)

Status Code:
0 Connection not established
200 Ok
401 Unauthorized
403 Forbidden
404 Not Found
500 Internal Server Error

'''

def device_details(url, id, token):
	headers = {"Authorization":"Bearer " + token}

	try:
		r = requests.get(url+"/devices/"+id, headers=headers)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0,0

	return r.status_code,r.text



'''
Updates device details

parameters: url of web service, device id, account access token,
new name to device, new description to device, new secret password.

returns a tuple (status code, json message)
status_code:
0 if could not connect to url, esle return status code:
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
500 Internal Server Error

'''
def update_device(url, id, token, new_name, new_description, new_secret):
	headers = {"Authorization":"Bearer " + token, 'content-type': 'application/json'}
	body = {"name":new_name,"description":new_description,"secret":new_secret}

	try:
		r = requests.put(url+"/devices/"+id, headers=headers, json=body)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0,0
	
	return r.status_code, r.text



'''
Remove device

parameters: url of web service, device id, account access token

returns a tuple (status code, json message)
status_code:
0 if could not connect to url, esle return status code:
204 No Content
401 Unauthorized
403 Forbidden
404 Not Found
500 Internal Server Error

'''

def remove_device(url, dev_id, token):
	headers = {"Authorization":"Bearer " + token}
	
	try:
		r = requests.delete(url+"/devices/"+dev_id, headers=headers)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0,0
	
	return r.status_code, r.text



'''
Create device data stream

parameters: url of web service, account_token, device id, stream name

returns a tuple (status code, json message)
status_code:
0 if could not connect to url
204 No Content
403 Forbidden
401 Unauthorized
404 Not Found
400 Bad Request
500 Internal Server Error
'''

def create_stream(url, account_token, device_id, stream_name):
	headers = {"Authorization":"Bearer " + account_token, 'content-type': 'application/json'}
	
	try:
		r = requests.put(url+"/devices/"+device_id+"/streams/"+stream_name, headers=headers)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0,0
	
	return r.status_code, r.text



'''
Published data into stream

parameters: url of web service, device token, device id, stream name,
timestamp, value, ttl

timestamp - Timestamp associated with the published value (ISO 8601, yyyy-MM-dd'T'HH:mm:ss.SSS'Z). If omitted,
timestamp at reception moment will be assumed.
value - The value to be publish into the stream
ttl - How long this value is valid (optional). This value has no meaning inside the platform, however may be used by data
consumers.

returns a tuple (status code, json message)
status_code:
0 if could not connect to url
201 Created
403 Forbidden
401 Unauthorized
404 Not Found (o device ou a stream nao existe)
400 Bad Request
500 Internal Server Error
'''
def publish_into_stream(url, device_token, device_id, stream_name, timestamp, value, ttl):
	headers = {"Authorization":"Bearer " + device_token, 'content-type': 'application/json'}
	data = {"timestamp":timestamp, "value":value, "ttl":ttl}

	try:
		r = requests.post(url+"/devices/"+device_id+"/streams/"+stream_name+"/value", headers=headers, json=data)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0,0

	return r.status_code, r.text



'''
Read data from a device stream

parameters: url of web service, account or device token, device token, device id,
stream name, start date and end date of query (ISO 8601 timestamp)

returns a tuple (status code, json message)
status_code:
0 if could not connect to url
200 Ok
403 Forbidden
401 Unauthorized
404 Not Found (device ou stream inexistente)
500 Internal Server Error
'''

def read_stream(url, token, device_id, stream_name, start, end):
	headers = {"Authorization":"Bearer " + token}
	
	try:
		r = requests.get(url+"/devices/"+device_id+"/streams/"+stream_name+"/values/?start="+start+"&end="+end, headers=headers)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0,0
	
	return r.status_code, r.text
	


'''
Removes a device stream

params: url of web service, account token, device id, stream name

returns a tuple (status code, json message)
status_code:
0 if could not connect to url
204 No Content
403 Forbidden
401 Unauthorized
404 Not Found (device ou stream inexistente)
500 Internal Server Error
'''
def remove_stream(url, account_token, device_id, stream_name):
	headers = {"Authorization":"Bearer " + account_token}
	
	try:
		r = requests.delete(url+"/devices/"+device_id+"/streams/"+stream_name, headers=headers)
	except requests.exceptions.RequestException as e:
		print >>sys.stderr, e
		return 0,0

	return r.status_code, r.text



'''
List device streams

params: url of web service, account token, device id


returns a tuple (status code, json message)
status_code:
0 if could not connect to url
200 Ok
403 Forbidden
401 Unauthorized
404 Not Found (device ou stream inexistente)
500 Internal Server Error
'''
def list_streams(url, account_token, device_id):
	headers = {"Authorization":"Bearer " + account_token, 'content-type': 'application/json'}
	try:
		r = requests.get(url+"/devices/"+device_id+"/streams", headers=headers)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0,0

	return r.status_code, r.text



'''
Creates subscription

parameters: url of web service, account token, name, description, subscriber id, device id,
stream name, state, retention count, retention time, retries, retry policy and point of contact(optional)

name - Subscription name (required)
description - (optional)
subscriber_id - The subscriber id (ex. Device id that is interested in the data)
stream - Stream name that we want to subscribe
state - Subscription state (active | suspended) (optional. By default all subscriptions are created in the "active" status)
point_of_contact - URL where SmartIoT should deliver new data. If this parameter is omitted, then data should be consumed
via polling.
device_id - Device id that owns the stream.
retention_count - Quantity of records to keep in the associated subscription before discarding the old records not consumed
or delivered. (default / currently is unlimited)
retention_time - Maximum amount of time to keep data in the associated subscription before discarding oold records not
consumed or delivered. (default / currently is unlimited)
retries - Numbner of delivery retries (default = 5)
retry_policy - Interval between delivery attempts. (ex. If retry policy is "30,45,60" and first attempt fails, then SmartIoT will try
a second delivery after 30 seconds. Next retry (third), will occur after 45 seconds. Subsequent retries will happen is 60
seconds intervals utils the rettries value is reached. By default the retry policy is "30,45,60" seconds. Retry policy should be
specified in the format " (number)(,number)* ". If you specify an invalid retry policy, the a status code 400 will be returned.

returns a tuple (status code, json message)
status_code:
0 if could not connect to url
201 Created
403 Forbidden
401 Unauthorized
404 Not Found
400 Bad Request
500 Internal Server Error
'''

def create_subscription(url, account_token, name, description, subs_id, device_id, stream_name, state,
						retention_count, retention_time, retries, retry_policy, point_of_contact=None):
	headers = {"Authorization":"Bearer " + account_token, 'content-type': 'application/json'}
	body = {"name":name, "description":description, "subscriber_id":subs_id, "device_id":device_id,
	"stream":stream_name, "state":state, "retention_time":retention_time, "retention_count":retention_count,
	"retries":retries, "retry_policy":retry_policy}

	if point_of_contact!=None:
		body["point_of_contact"] = point_of_contact

	try:
		r = requests.post(url+"/subscriptions", headers=headers, json=body)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0,0

	return r.status_code, r.text



'''
Get subscription details

parameters: url of web service, account token, subscription id

returns a tuple (status code, content)

Status code:
0   Could not establish connection
200 Ok
403 Forbidden
401 Unauthorized
404 Not Found
500 Internal Server Error
'''
def get_subscription_details(url, account_token, subs_id):
	headers = {"Authorization":"Bearer " + account_token, 'content-type': 'application/json'}
	try:
		r = requests.get(url+"/subscriptions/"+subs_id, headers=headers)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0,0

	return r.status_code, r.text
	

'''
Updates subscription

parameters: url of web service, account token, subscription id,
name - Subscription name (required)
description - (optional)
state - Subscription state (active | suspended) (optional. By default all subscriptions are created in the "active" status)
point_of_contact - URL where SmartIoT should deliver new data. If this parameter is omitted, then data should be consumed
via polling.
retention_count - Quantity of records to keep in the associated subscription before discarding the old records not consumed
or delivered. (default / currently is unlimited)
retention_time - Maximum amount of time to keep data in the associated subscription before discarding oold records not
consumed or delivered. (default / currently is unlimited)
retries - Numbner of delivery retries (default = 5)
retry_policy - Interval between delivery attempts. (ex. If retry policy is "30,45,60" and first attempt fails, then SmartIoT will try
a second delivery after 30 seconds. Next retry (third), will occur after 45 seconds. Subsequent retries will happen is 60
seconds intervals utils the rettries value is reached. By default the retry policy is "30,45,60" seconds. Retry policy should be
specified in the format " (number)(,number)* ". If you specify an invalid retry policy, the a status code 400 will be returned.

return a tuple (status code, content)

Status code:
0   Could not establish connection
204 No Content
403 Forbidden
401 Unauthorized
404 Not Found (subscription nao existente)
400 Bad Request
500 Internal Server Error

'''

def update_subscription(url, account_token, subs_id, new_name, new_desc, new_status, retention_count, retention_time, retries, retry_policy, point_of_contact=None):
	headers = {"Authorization":"Bearer " + account_token, 'content-type': 'application/json'}
	body = {"name":new_name, "description":new_desc,"status":new_status, "retention_time":retention_time, "retention_count":retention_count,
	"retries":retries, "retry_policy":retry_policy}

	if point_of_contact!=None:
		body["point_of_contact"] = point_of_contact

	try:
		r = requests.put(url+"/subscriptions/"+subs_id, headers=headers, json=body)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0,0

	return r.status_code, r.text
	
'''
Remove subscription

parameters: url of Web Service, account token, subscription id

return a tuple (status code, content)

Status code:
0   Could not establish connection
204 No Content
403 Forbidden
401 Unauthorized
404 Not Found (subscription nao existente)
400 Bad Request
500 Internal Server Error
'''

def remove_subscription(url, account_token, subs_id):
	headers = {"Authorization":"Bearer " + account_token}
	
	try:
		r = requests.delete(url+"/subscriptions/"+subs_id, headers=headers)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0,0

	return r.status_code, r.text


'''
Retrieve subscription values

parameters: url of web service, token of device, subscription id

returns the content of subscription

return a tuple (status code, content)

Status code:
0   Could not establish connection
200 Ok
403 Forbidden
401 Unauthorized
404 Not Found
500 Internal Server Error

'''

def retrieve_subscription_values(url, device_token, subs_id):
	headers = {"Authorization":"Bearer " + device_token, 'content-type': 'application/json'}
	
	try:
		r = requests.get(url+"/subscriptions/"+subs_id+"/values", headers=headers)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0,0

	return r.status_code, r.text

