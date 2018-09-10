from __future__ import absolute_import, unicode_literals
from celery.decorators import periodic_task
from celery import shared_task
from datetime import timedelta
import datetime
from django.utils import timezone, dateparse
import dateutil.parser
import json
import local_broker_interface as lb
import smartIoT_Interface as sm
from server.mainserver.models import Subscription, Value, Sensor, Alarm, day_week, Triggered_alarm, AlarmActuator, Localization, Sensorsubtype
import pytz
from fcm_django.models import FCMDevice


# period of periodic task in seconds
period = 15

# Authentication of server
device_id = "server"
device_password = "debug_mode"


# Test sending data to SmartIoT
'''
@periodic_task(run_every=timedelta(seconds=period))
def test_send():
	device_id = "server-send"
	device_password = "debug_mode_send"
	device_name = "server_send"
	stream_name = "server_test"

	token = sm.authenticate("https://iot.alticelabs.com","ua1", "8ik8fm0h8mqer821agae3qg29ve1kl84d9b0svsiesqj52lil59g")
	print(token)

	if token[0] != 201:
		return token
	token = token[1]

	auth = sm.device_authentication("https://iot.alticelabs.com", device_id, device_password)
	print(auth)

	if auth[0] != 201:
		return auth

	publ = sm.publish_into_stream("https://iot.alticelabs.com", auth[1], device_id, stream_name, "2016-09-10T19:15:00.325Z", 100, 300)
	print(publ)

	if token[0] != 201:
		return publ
	return (200, {"status":"Success"})
'''

@shared_task
def send_notification_bulk(title, body):
	devices = FCMDevice.objects.all()
	devices.send_message(title=title, body=body, icon="alert", click_action="/alerts")


def reg_device(device_id, device_password, device_name, device_description, device_type, device_lat, device_lon):
	
	token = sm.authenticate("https://iot.alticelabs.com","ua1", "8ik8fm0h8mqer821agae3qg29ve1kl84d9b0svsiesqj52lil59g")

	if token[0] != 201:
		print token
		return False
	token = token[1]

	reg = sm.register_device("https://iot.alticelabs.com", device_id, device_password, token, device_name, device_description)
	if reg[0]!=201:
		print reg
		return False
	
	loc = Localization(lat=device_lat, lon=device_lon)
	loc.save()

	s = Sensor(device_id=device_id, name=device_name, date_added=datetime.datetime.now(), information=device_description, sensor_type=device_type, active=True, localization=loc, state=Sensor.NOT_SEEN)
	s.save()

	return True

def add_stream(sensor_id, subtype, subs_name, subs_description, point_of_contact=None):

	token = sm.authenticate("https://iot.alticelabs.com","ua1", "8ik8fm0h8mqer821agae3qg29ve1kl84d9b0svsiesqj52lil59g")

	if token[0] != 201:
		print token
		return False
	token = token[1]

	# Create Stream on SmartIoT
	st = sm.create_stream("https://iot.alticelabs.com", token, sensor_id, subs_name)
	if st[0] != 204:
		print st
		return False

	# Create subscription
	sub = create_subscription(subs_name, subs_description, sensor_id, subs_name, point_of_contact)
	if sub[0] != 201:
		print sub
		return False


	sub_id = json.loads(sub[1])["id"]

	sen = Sensor.objects.get(device_id=sensor_id)

	subtype = Sensorsubtype.objects.get(name=subtype)

	new_sub = Subscription(subscription_id=sub_id, name=subs_name, date_added=datetime.datetime.now(), working=True, sender=True, subtype=subtype, sensor=sen)
	new_sub.save()

	return True

def send_data(device2_id, stream_name, value):

	token = sm.authenticate("https://iot.alticelabs.com","ua1", "8ik8fm0h8mqer821agae3qg29ve1kl84d9b0svsiesqj52lil59g")

	if token[0] != 201:
		print token
		return token
	token = token[1]

	auth = sm.device_authentication("https://iot.alticelabs.com", device_id, device_password)

	if auth[0] != 201:
		print auth
		return auth

	publ = sm.publish_into_stream("https://iot.alticelabs.com", auth[1], device2_id, stream_name, timezone.now().isoformat(), value, 3600)
	print publ

	if token[0] != 201:
		return publ
	
	return (200, {"status":"Success"})

def week_day(day):
	if day==day_week.MONDAY:
		return 0
	if day==day_week.TUESDAY:
		return 1
	if day==day_week.WEDNESDAY:
		return 2
	if day==day_week.THURSDAY:
		return 3
	if day==day_week.FRIDAY:
		return 4
	if day==day_week.SATURDAY:
		return 5
	if day==day_week.SUNDAY:
		return 6


def check_rules():
	rules = Alarm.objects.filter(state=Alarm.ACTIVE, has_threshold=False)

	# Check if alert is valid
	current_time = datetime.datetime.now()

	for rule in rules:
		triggered = False

		if rule.beg_date<current_time and rule.end_date>current_time:

			# Check if is valid for week day
			weekd = rule.daysOfWeek.all()
			if len(weekd)==0 or current_time.weekday() in [week_day(day.day) for day in weekd]:
				
				# Check if end hour is on same day that beginning hour
				if rule.hours_active_beg.hour>rule.hours_active_beg.hour or rule.hours_active_beg.hour==rule.hours_active_beg.hour and rule.hours_active_beg.minute>=rule.hours_active_end.minute:
					# Check if rule is being triggered
					if (current_time.hour>rule.hours_active_beg.hour or current_time.hour==rule.hours_active_beg.hour and current_time.minute>=rule.hours_active_beg.minute) or (current_time.hour<rule.hours_active_end.hour or current_time.hour==rule.hours_active_end.hour and current_time.minute<=rule.hours_active_end.minute):
						triggered = True
						ta, created = Triggered_alarm.objects.get_or_create(alarm=rule, state=Triggered_alarm.ACTIVE)

						# If it was triggered, send data to actuators
						
						# The line below is commented, for the server to ALWAYS send the actuator when he runs the task, not only on first time.
						if created:
						
							# Get all actuators associated with the alarm
							actuators = AlarmActuator.objects.filter(alarm=rule)
											
							for a in actuators:
								# Get all streams
								streams = a.subscriptions.all()
								for st in streams:
									# Send data to streams
									ret = send_data(st.sensor.device_id, st.name, a.value)
									if ret[0] != 200:
										print ret
									else:
										v = Value(data=a.value, timeToLive=3600, date=datetime.datetime.now().isoformat(), subscription=st)
										v.save()
										#ta.value.add(v)
				else:
					if (current_time.hour>rule.hours_active_beg.hour or (current_time.hour==rule.hours_active_beg.hour and current_time.minute>=rule.hours_active_beg.minute)) and (current_time.hour<rule.hours_active_end.hour or (current_time.hour==rule.hours_active_end.hour and current_time.minute<=rule.hours_active_end.minute)):
						triggered = True
						ta, created = Triggered_alarm.objects.get_or_create(alarm=rule, state=Triggered_alarm.ACTIVE)
						ta.value.add(m)
						
						# If it was triggered, send data to actuators
						# The line below is commented, for the server to ALWAYS send the actuator when he runs the task, not only on first time.
						if created:
						
							# Get all actuators associated with the rule
							actuators = AlarmActuator.objects.filter(alarm=rule)
											
							for a in actuators:
								# Get all streams
								streams = a.subscriptions.all()
								for st in streams:
									# Send data to streams
									ret = send_data(st.sensor.device_id, st.name, a.value)
									if ret[0] != 200:
										print ret
									else:
										v = Value(data=a.value, timeToLive=3600, date=datetime.datetime.now().isoformat(), subscription=st)
										v.save()
		if not triggered:
			tas = Triggered_alarm.objects.filter(alarm=rule, state=Triggered_alarm.ACTIVE)
			for ta in tas:
				ta.state=Triggered_alarm.NOT_SEEN
				ta.save()


def check_alerts(subscription_id, m):
	# Change state of alarms
	alarms = Alarm.objects.filter(state=Alarm.ACTIVE, has_threshold=True)
	
	for al in alarms:

		# Check if subscription is in current alert list
		if subscription_id in [sub.subscription_id for a in alarms for sub in al.subscriptions.all()]:
			triggered = False

			# Check if alarm is valid
			current_time = datetime.datetime.now()

			if al.beg_date<current_time and al.end_date>current_time:

				# Check if it has threshold, and if it violates it
				if (not al.has_threshold or al.type_alarm==Alarm.MAX and float(m.data)>al.threshold) or (al.type_alarm==Alarm.MIN and float(m.data)<al.threshold):
					# Check if is valid for week day
					weekd = al.daysOfWeek.all()

					if len(weekd)==0 or current_time.weekday() in [week_day(day.day) for day in weekd]:
												
						# Check if end hour is on same day that beginning hour
						if al.hours_active_beg.hour>al.hours_active_beg.hour or al.hours_active_beg.hour==al.hours_active_beg.hour and al.hours_active_beg.minute>=al.hours_active_end.minute:
							if (current_time.hour>al.hours_active_beg.hour or current_time.hour==al.hours_active_beg.hour and current_time.minute>=al.hours_active_beg.minute) or (current_time.hour<al.hours_active_end.hour or current_time.hour==al.hours_active_end.hour and current_time.minute<=al.hours_active_end.minute):
								triggered = True
								ta, created = Triggered_alarm.objects.get_or_create(alarm=al, state=Triggered_alarm.ACTIVE)
								ta.value.add(m)
								# If it was triggered, send data to actuators
								if created:
									send_notification_bulk.delay(al.name+" Triggered", al.name+" triggered by the sensor "+m.subscription.sensor.name+" with value "+str(round(float(m.data),2)))
									# Get all actuators associated with the alarm
									actuators = AlarmActuator.objects.filter(alarm=al)
									
									for a in actuators:
										# Get all streams
										streams = a.subscriptions.all()
										for st in streams:
											# Send data to streams
											ret = send_data(st.sensor.device_id, st.name, a.value)
											if ret[0] != 200:
												print ret
						else:
							if (current_time.hour>al.hours_active_beg.hour or (current_time.hour==al.hours_active_beg.hour and current_time.minute>=al.hours_active_beg.minute)) and (current_time.hour<al.hours_active_end.hour or (current_time.hour==al.hours_active_end.hour and current_time.minute<=al.hours_active_end.minute)):
								triggered = True
								ta, created = Triggered_alarm.objects.get_or_create(alarm=al, state=Triggered_alarm.ACTIVE)
								ta.value.add(m)
								# If it was triggered, send data to actuators
								if created:
									send_notification_bulk.delay(al.name+" Triggered", al.name+" triggered by the sensor "+m.subscription.sensor.name+" with value "+str(round(float(m.data),2)))
									# Get all actuators associated to the alarm
									actuators = AlarmActuator.objects.filter(alarm=al)
									
									for a in actuators:
										# Get all streams
										streams = a.subscriptions.all()
										for st in streams:
											# Send data to streams
											ret = send_data(st.sensor.device_id, st.name, a.value)
											if ret[0] != 200:
												print ret
			if not triggered:
				tas = Triggered_alarm.objects.filter(alarm=al, state=Triggered_alarm.ACTIVE)
				for ta in tas:
					ta.state=Triggered_alarm.NOT_SEEN
					ta.save()

# Receive data from subscription of SmartIoT
@periodic_task(run_every=timedelta(seconds=period))
def receive_data():

	# Get all subscription_id and sensor
	subscriptions = Subscription.objects.values('subscription_id', 'sensor', 'working', 'subtype').filter(sender=True)

	token = sm.authenticate("https://iot.alticelabs.com","ua1", "8ik8fm0h8mqer821agae3qg29ve1kl84d9b0svsiesqj52lil59g")

	if token[0] != 201:
		print token
		return token
	token = token[1]

	auth = sm.device_authentication("https://iot.alticelabs.com", device_id, device_password)

	if auth[0] != 201:
		print auth
		return auth

	try:
		for subscription in subscriptions:
			sensor = Sensor.objects.get(device_id=subscription['sensor'])
			# Check if sensor is active
			if sensor.active:
				
				ret = sm.retrieve_subscription_values("https://iot.alticelabs.com", auth[1], subscription['subscription_id'])

				if ret[0]!=200:
					print ret

				else:
					try:
						content = json.loads(ret[1])["values"]
						for value in content:
							# It is needed to sum two hours, because of SmartIoT timezone
							dt = (dateparse.parse_datetime(value["createdAt"])+timedelta(hours=2))
							dt = dt.replace(tzinfo=None)
							m = Value(data=value["data"], timeToLive=value["timeToLive"], date=dt, subscription=Subscription.objects.get(subscription_id=subscription['subscription_id']))
							m.save()
							
							if Subscription.objects.get(subscription_id=subscription['subscription_id']).subtype.name==Sensorsubtype.LATITUDE:
								sensor.localization = Localization.objects.get_or_create(lat=value["data"], lon=sensor.localization.lon)[0]
								sensor.save()

							if Subscription.objects.get(subscription_id=subscription['subscription_id']).subtype.name==Sensorsubtype.LONGITUDE:
								sensor.localization = Localization.objects.get_or_create(lat=sensor.localization.lat, lon=value["data"])[0]
								sensor.save()

							if (subscription["working"]==False):
								new_state = Subscription.objects.get(subscription_id=subscription['subscription_id'])
								new_state.working = True
								new_state.save()

							check_alerts(subscription["subscription_id"], m)

						
						# If no value is returned, turn subscription off
						if len(content) == 0:
							if (subscription["working"]==True):
								new_state = Subscription.objects.get(subscription_id=subscription['subscription_id'])
								new_state.working = False
								new_state.save()

					
					except Exception as e:
						print(e)

	except Exception as e:
		print(e)

	# Get all triggered alerts. If all subscriptions are not working, set state as not seen
	alarms = Alarm.objects.filter(state=Alarm.ACTIVE, has_threshold=True)
	
	for al in alarms:
		if all([sub.working==False for sub in al.subscriptions.all()]):
			tas = Triggered_alarm.objects.filter(alarm=al, state=Triggered_alarm.ACTIVE)

			for ta in tas:
				if ta.state==Triggered_alarm.ACTIVE:
					ta.state=Triggered_alarm.NOT_SEEN
					ta.save()

	check_rules()

	return (200, {"status":"Success"})


def create_subscription(subs_name, subs_desc, sender_device_id, stream_name, point_of_contact=None):

	token = sm.authenticate("https://iot.alticelabs.com","ua1", "8ik8fm0h8mqer821agae3qg29ve1kl84d9b0svsiesqj52lil59g")
	
	if token[0] != 201:
		return token

	token = token[1]

	subs = sm.create_subscription("https://iot.alticelabs.com", token, subs_name, subs_desc, "server", sender_device_id, stream_name, "active", 10, 3600, 5, "30,45,60", point_of_contact)
	print(subs)

	return subs

# Update all subscriptions
def update_subs():

	subscriptions = Subscription.objects.all()

	for sub in subscriptions:
		token = sm.authenticate("https://iot.alticelabs.com","ua1", "8ik8fm0h8mqer821agae3qg29ve1kl84d9b0svsiesqj52lil59g")
	
		if token[0] != 201:
			return token

		token = token[1]

		
		up = sm.update_subscription("https://iot.alticelabs.com", token, sub.subscription_id, sub.name, "description", "active", 12, 3600, 15, "30,45,60,120", None)
		print up

## Only for testing purposes with local broker

'''
@periodic_task(run_every=timedelta(seconds=120))
def local_test_send():
	print('periodic task -> Send data to local broker')

	subs_id = "teste"

	create = lb.create_stream("127.0.0.1:8001", "teste", subs_id)
	
	if create[0]!=200:
		return create[1]
	
	r = lb.send_data("127.0.0.1:8001", "teste", subs_id, timezone.now().isoformat(), 10, 10)
	
	if r[0]!=200:
		return r[1]

@periodic_task(run_every=timedelta(seconds=120))
def local_test_receive():
	print('periodic task -> Receive data from local broker and save on database')

	subs_id = "teste"
	time = timezone.now()
	value = 0

	r = lb.read_data("127.0.0.1:8001", "teste", subs_id)
	if r[0]!=200:
		return r[1]

	try:
		content = json.loads(r[1])["values"]
		for value in content:
			print(value)
	except Exception as e:
		print(e)
'''

## Helper that indicates how to authenticate, create two devices, create a stream and subscribe it
'''
def create():

	device_id = "server-send"
	device_password = "debug_mode_send"
	device_name = "server_send"
	device_description = "IoTCity Server-sender"

	stream_name = "server_test"

	subs_name = "subscription_test2"
	subs_desc = "Subscription to server"

	device2_id = "server"
	device2_password = "debug_mode"

	token = sm.authenticate("https://iot.alticelabs.com","ua1", "8ik8fm0h8mqer821agae3qg29ve1kl84d9b0svsiesqj52lil59g")
	

	if token[0] != 201:
		return token

	token = token[1]


	dev = sm.register_device("https://iot.alticelabs.com", device_id, device_password, token, device_name, device_description)
	print(dev)

	if dev[0] != 201:
		return dev

	dev = sm.register_device("https://iot.alticelabs.com", device2_id, device2_password, token, device_name, device_description)
	print(dev)

	if dev[0] != 201:
		return dev

	auth = sm.device_authentication("https://iot.alticelabs.com", device_id, device_password)
	print(auth)

	if auth[0] != 201:
		return auth

	create = sm.create_stream("https://iot.alticelabs.com", token, device_id, stream_name)
	print(create)

	if create[0] != 204:
		return create

	lis = sm.list_streams("https://iot.alticelabs.com", token, device_id)
	print(lis)

	if lis[0] != 200:
		return lis

	stream_id = json.loads(lis[1])["streams"][0]["id"]

	subs = sm.create_subscription("https://iot.alticelabs.com", token, subs_name, subs_desc, device2_id, device_id, stream_name, "active", 10, 3600, 5, "30,45,60")
	print(subs)

	if subs[0] != 201:
		return lis

	subscription_id = json.loads(subs[1])["id"]
	
	return subscription_id
'''