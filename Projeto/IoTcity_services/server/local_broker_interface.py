import requests
import sys

def create_stream(url, secret, name_stream):
	headers = {"Authorization":"Bearer " + secret, 'content-type': 'application/json'}
	
	try:
		r = requests.post("http://"+url+"/streams/"+name_stream+"/create", headers=headers)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0
	
	return r.status_code, r.text

def send_data(url, secret, name_stream, timestamp, value, ttl):
	headers = {"Authorization":"Bearer " + secret, 'content-type': 'application/json'}
	body = {"timestamp":timestamp, "value":value, "ttl":ttl}
	try:
		r = requests.post("http://"+url+"/streams/"+name_stream+"/send", headers=headers, json=body)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0

	return r.status_code, r.text

def read_data(url, secret, name_stream):
	headers = {"Authorization":"Bearer " + secret, 'content-type': 'application/json'}

	try:
		r = requests.get("http://"+url+"/streams/"+name_stream+"/values", headers=headers)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0

	return r.status_code, r.text
	

def subscribe(url, secret, name_stream, point_of_contact):
	headers = {"Authorization":"Bearer " + secret, 'content-type': 'application/json'}
	body = {"point_of_contact":point_of_contact}
	
	try:
		r = requests.post("http://"+url+"/streams/"+name_stream+"/subscribe", headers=headers, json=body)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0

	return r.status_code, r.text

def delete_stream(url, secret, name_stream):
	headers = {"Authorization":"Bearer " + secret, 'content-type': 'application/json'}
	
	try:
		r = requests.delete("http://"+url+"/streams/"+name_stream+"/delete", headers=headers)
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, e
		return 0
		
	return r.status_code, r.text
	
def test():
	print(create_stream("127.0.0.1:8000", "teste", "temperature"))
	print(send_data("127.0.0.1:8000", "teste", "temperature", "15", "15", "2"))
	print(subscribe("127.0.0.1:8000", "teste", "temperature", "http://putsreq.com/3hQofDdlUPG6IC1qgoIp"))
	print(subscribe("127.0.0.1:8000", "teste", "temperature", "http://putsreq.com/peGjst7CNQKGSUatb2qS"))
	print(subscribe("127.0.0.1:8000", "teste", "temperature", "http://putsreq.com/1Xn0wtJUdkPay8pAEoxB"))
	print(send_data("127.0.0.1:8000", "teste", "temperature", "15", "30", "2"))
	print(read_data("127.0.0.1:8000", "teste", "temperature"))
	print(read_data("127.0.0.1:8000", "teste", "temperature"))
	print(delete_stream("127.0.0.1:8000", "teste", "temperature"))
