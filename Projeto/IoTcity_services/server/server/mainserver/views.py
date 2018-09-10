from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.utils import timezone, dateparse
from django.urls import reverse
from models import Sensor, Localization, Subscription, Value, Subscription_Group, Alarm, day_week, UserReport, Triggered_alarm, Note, AlarmActuator, Sensorsubtype, ReportAttach
from forms import AlarmForm, NoteForm, ActuatorForm, RuleForm
from django.db.models import Q
from math import radians, cos, sin, asin, sqrt
import requests
import tempfile
from django.core import files
from datetime import timedelta

import collections
import os
import magic
import tasks
import json
import datetime
import sys



def login(request):
	return render(request, 'adminlte/login.html', {})

# If the sensor is turned off, the values will NOT appear on the index
@login_required(login_url="login")
def index(request, success=None):

	subscriptions = []
	alerts = []
	triggered_alerts = []
	active_alerts = []
	reports_dict = []
	sensors = []

	# Get the allowed subscriptions
	subscriptions = get_subscriptions(request.user)

	for s in subscriptions:
		alerts += Alarm.objects.filter(subscriptions=s.subscription_id, state=Alarm.ACTIVE, user=request.user)

		# All the User Reports associated to the subscription, except the seen, ordeered by date
		reports = UserReport.objects.filter(Q(deleted=False) &  (Q(working_state=UserReport.WORKING_ON_IT) | Q(working_state=UserReport.WAITING)) & Q(subscription=s)).order_by('-date')

		reports_dict += [{"id":report.id, "state":dict(UserReport.TYPE_CHOICES)[report.state], "working_state":dict(UserReport.WORKING_CHOICES)[report.working_state], "information":report.information, "date":report.date, "stream":report.subscription.name, "email":report.email, "title":report.title, "name": report.user_name, "sen_name":report.subscription.sensor.name, "sen_type":report.subscription.sensor.sensor_type, "sen_id":report.subscription.sensor.device_id } for report in reports]
		
		sensor = Sensor.objects.get(name=s.sensor)
		if sensor.device_id not in [sen["id"] for sen in sensors]:
			sensors += [{"id":sensor.device_id, "name":sensor.name, "type": sensor.sensor_type, "streams":1, "working":1 if s.working else 0, "status":sensor.active, "inactivestreams":[] if s.working else [s.name]}]

		else:
			sens = [sen for sen in sensors if sen["id"]==sensor.device_id][0]
			if s.working:
				sens["working"] += 1
			else:
				sens["inactivestreams"] += [s.name]

			sens["streams"] += 1


	# All the active alarms and
	# All the alarms that were active, but the user did not saw
	for alert in alerts:
		triggered_alerts += Triggered_alarm.objects.filter(alarm=alert, state=Triggered_alarm.NOT_SEEN, alarm__user=request.user, deleted=False)
		active_alerts += Triggered_alarm.objects.filter(alarm=alert, state=Triggered_alarm.ACTIVE, alarm__user=request.user, deleted=False)
	
	alerts_dict = []

	for alert in triggered_alerts+active_alerts:
		if alert.id not in [al["id"] for al in alerts_dict]:

			value = alert.value.earliest('date')

			end_date = "-"
			peak = None
			peak_date = None

			
			if alert.alarm.type_alarm==Alarm.MAX:
				x = reduce(lambda x,y: x if float(x['data'])>float(y['data']) else y, alert.value.values('data','date'))
				peak = round(x['data'],2)
				peak_date = x['date']
			elif alert.alarm.type_alarm==Alarm.MIN:
				x = reduce(lambda x,y: x if float(x['data'])<float(y['data']) else y, alert.value.values('data', 'date'))
				peak = round(x['data'],2)
				peak_date = x['date']

			if alert.state != Triggered_alarm.ACTIVE:
				x = reduce(lambda x,y: x if x['date']>y['date'] else y, alert.value.values('date'))
				end_date = x["date"]

			alert_types = list(set([sub.sensor.sensor_type for sub in alert.alarm.subscriptions.all()]))
			sens = list(set([sub.sensor for sub in alert.alarm.subscriptions.all()]))

			alerts_dict += [{"id":alert.id, "alert_id":alert.alarm.id, "name":alert.alarm.name, "state":dict(Triggered_alarm.STATE_CHOICES)[alert.state],  "start_date":value.date, "end_date":end_date, "peak":peak, "peak_date":peak_date, "types":alert_types, "sens":sens}]

			if alert.alarm.type_alarm != None:
				alerts_dict[-1]["maximum_minimum"] = dict(Alarm.ALARM_CHOICES)[alert.alarm.type_alarm]
				alerts_dict[-1]["threshold"] = alert.alarm.threshold

	# Sort alerts by start date
	alerts_dict = sorted(alerts_dict, key=lambda d: d['start_date'], reverse=True)

	# All the notes associated to the user, ordered by date of end
	notes = Note.objects.filter(user=request.user, state=Note.ACTIVE, date_end__gt=datetime.datetime.now()).order_by('date_end')
	
	notes_dict = [{"id":note.id, "name":note.name, "beg": note.date_beginning, "end":note.date_end, "description":note.information} for note in notes]

	form = NoteForm()

	calc = index_calculations(subscriptions)

	response = calc.copy()
	response.update({"alerts":alerts_dict, "reports":reports_dict, "notes":notes_dict, "form":form, "success":success, "sensors":sensors, "user_types":get_types(request)})

	return render(request, 'adminlte/index.html', response)


# Get all the sensors from the subscription allowed and send the information to the view
@login_required(login_url="login")
def map(request):

	sen_list = []
	subscriptions = []
	sensors = {}

	# Get the allowed subscriptions
	# And the sensor related
	subscriptions = get_subscriptions(request.user)

	for subsc in subscriptions:
		if subsc.subtype.name != Sensorsubtype.LATITUDE and subsc.subtype.name != Sensorsubtype.LONGITUDE:
			sensor = Sensor.objects.get(name=subsc.sensor)
			if sensor in sensors:
				sensors[sensor] += [subsc]
			else:
				sensors[sensor] = [subsc]

		

	# For all the sensors with allowed subscriptions
	for sensor in sensors:
		working = 0
		not_working = 0
		temp_values = []
		subscriptions = []

		for s in sensors[Sensor.objects.get(name=sensor)]:
			
			subscriptions+=[s.name]
			if s.working:
				working += 1
			else:
				not_working += 1


			val = Value.objects.filter(subscription=s.subscription_id)


			if val.exists():
				temp_values += [(s.name, round(val.latest('date').data,2), val.latest('date').date.strftime("%s %s" % ("%d-%m-%Y" , "%H:%M:%S")))]
			

		sen_list += [{"id":sensor.device_id, "name":sensor.name, "information":sensor.information, "type":sensor.sensor_type, "lat": Localization.objects.get(pk=sensor.localization.id).lat, "lon": Localization.objects.get(pk=sensor.localization.id).lon, "active":working, "all":not_working+working,
		"value":temp_values, "turned_on":sensor.active, "address":sensor.localization.address, "all_streams":subscriptions}]



	sensors = json.dumps(sen_list)
	return render(request, 'adminlte/map.html', {"sensors":sensors, "sensors2":sen_list, "user_types":get_types(request)})


@login_required(login_url="login")
def temperature(request, weeks=None, days=None, hours=None):
	
	sen_list, values = get_temp_data(request.user, weeks, days, hours)	

	return render(request, 'adminlte/temperature.html', {"sensors":sen_list, "values":json.dumps(values), "user_types":get_types(request)})

@login_required(login_url="login")
def lighting(request, days=None, weeks=None, hours=None):	
	sen_list, ill_values, act_values = get_lighting_data(request.user, weeks, days, hours)	

	return render(request, 'adminlte/illumination.html', {"sensors":sen_list, "ill":json.dumps(ill_values), "act":json.dumps(act_values), "user_types":get_types(request)})

@login_required(login_url="login")
def air(request, days=None, weeks=None, hours=None):	
	sen_list, pressure_values, co2_values = get_air_data(request.user, weeks, days, hours)

	return render(request, 'adminlte/air.html', {"sensors":sen_list, "pressure":json.dumps(pressure_values), "co2":json.dumps(co2_values), "user_types":get_types(request)})

@login_required(login_url="login")
def waste(request, weeks=None, days=None, hours=None):
	sen_list, values, values_temp_values, values_vol_values = get_waste_data(request.user, weeks, days, hours)

	return render(request, 'adminlte/waste.html', {"sensors":sen_list, "values":json.dumps(values), "temp":json.dumps(values_temp_values), "vol":json.dumps(values_vol_values), "user_types":get_types(request)})

@login_required(login_url="login")
def noise(request, weeks=None, days=None, hours=None):
	sen_list, values = get_noise_data(request.user, weeks, days, hours)

	return render(request, 'adminlte/sound.html', {"sensors":sen_list, "values":json.dumps(values), "user_types":get_types(request)})

@login_required(login_url="login")
def radiation(request, days=None, weeks=None, hours=None):
	sen_list, values, vis_values, red_values = get_radiation_data(request.user, weeks, days, hours)

	return render(request, 'adminlte/uvradiation.html', {"sensors":sen_list, "uv":json.dumps(values), "visible":json.dumps(vis_values), "infrared":json.dumps(red_values), "user_types":get_types(request)})

@login_required(login_url="login")
def people(request, days=None, weeks=None, hours=None):
	sen_list, values = get_people_data(request.user, weeks, days, hours)	

	return render(request, 'adminlte/people.html', {"sensors":sen_list, "values":json.dumps(values), "user_types":get_types(request)})

@login_required(login_url="login")
def reports(request):
	reports_dict = []
	reports_type = []

	# Get the allowed subscriptions
	subscriptions = get_subscriptions(request.user)
	for s in subscriptions:

		# All the User Reports associated to the subscription ordeered by date
		reports = UserReport.objects.filter(deleted=False, subscription=s).order_by('-date')
		reports_dict += [{"id":report.id, "state":dict(UserReport.TYPE_CHOICES)[report.state], "working_state":dict(UserReport.WORKING_CHOICES)[report.working_state], "information":report.information, "date":report.date, "stream":report.subscription.name, "email":report.email, "title":report.title, "name": report.user_name, "sen_name":report.subscription.sensor.name, "sen_type":report.subscription.sensor.sensor_type, "sen_id":report.subscription.sensor.device_id} for report in reports]
	

	return render(request, 'adminlte/reports.html', {"reports":reports_dict, "user_types":get_types(request)})

@login_required(login_url="login")
def read_report(request, id):
	try:
		UR = UserReport.objects.get(id=id)
	except Exception as e:
		print e
		raise Http404

	if UR.state==UserReport.NOT_SEEN:
		UR.state = UserReport.SEEN
		UR.save()

	# Get the allowed subscriptions
	subs = get_subscriptions(request.user)
	
	# Do not allow to read a report from a sensor not allowed
	if(UR.subscription.subscription_id not in [sub.subscription_id for sub in subs]):
		raise Http404
	return render(request, 'adminlte/read_report.html', {'report':UR, "sen_id":UR.subscription.sensor.device_id, "sen_name":UR.subscription.sensor.name, "stream":UR.subscription.name, "user_types":get_types(request)})

@login_required(login_url="login")
def alerts(request, success=None, id=-1):
		
	subscriptions = []
	alerts = []
	senders = []
	triggeredNotSeen_alerts = []
	triggeredActive_alerts = []
	all_alerts = []
	sensors = []
	not_sender = []

	if request.method=='GET':
		# Get the allowed subscriptions
		subs = get_subscriptions(request.user)

		for s in subs:
			subscriptions +=  (s.subscription_id, s.name),
			all_alerts += Alarm.objects.filter(subscriptions=s.subscription_id, user=request.user, state=Alarm.ACTIVE, has_threshold=True)

			if not s.sender:
				senders += [(s.subscription_id, s.name)]
			else:
				not_sender += [(s.subscription_id, s.name)]

		for alert in all_alerts:
			triggeredNotSeen_alerts += Triggered_alarm.objects.filter(alarm=alert, state=Triggered_alarm.NOT_SEEN, alarm__user=request.user, deleted=False)
			triggeredActive_alerts += Triggered_alarm.objects.filter(alarm=alert, state=Triggered_alarm.ACTIVE, alarm__user=request.user, deleted=False)

			name_subs = [su.name for su in alert.subscriptions.all()]
			daysWeek = 'All week' if alert.daysOfWeek.count()==7 or alert.daysOfWeek.count()==0 else ", ".join([ str(dict(day_week.DAYS_OF_WEEK)[day]) for day in alert.daysOfWeek.all().values_list('day', flat=True)])

			if alert.id not in [al["id"] for al in alerts]:
				alert_types = list(set([sub.sensor.sensor_type for sub in alert.subscriptions.all()]))
				sens = list(set([sub.sensor for sub in alert.subscriptions.all()]))
				
				alerts += [{"id":alert.id, 'subscription_name':", ".join(name_subs), 'name':alert.name, 'beg_date':alert.beg_date, 'end_date':alert.end_date, 'daysOfWeek':daysWeek, 'hours_act':alert.hours_active_beg, 'hours_beg':alert.hours_active_end, 'state': alert.state, 'types':alert_types, 'sens':sens}]
				if alert.type_alarm!=None:
					alerts[-1]['type_alarm'] = dict(alert.ALARM_CHOICES)[alert.type_alarm]

				if alert.threshold!=None:
					alerts[-1]['threshold'] = alert.threshold

		alerts_dict = []

		for alert in triggeredNotSeen_alerts+triggeredActive_alerts:

			if alert.id not in [al["id"] for al in alerts_dict]:

				value = alert.value.earliest('date')

				end_date = "-"
				peak = None
				peak_date = None

				if alert.alarm.type_alarm==Alarm.MAX:
					x = reduce(lambda x,y: x if float(x['data'])>float(y['data']) else y, alert.value.values('data','date'))
					peak = round(x['data'],2)
					peak_date = x['date']
				elif alert.alarm.type_alarm==Alarm.MIN:
					x = reduce(lambda x,y: x if float(x['data'])<float(y['data']) else y, alert.value.values('data','date'))
					peak = round(x['data'],2)
					peak_date = x['date']

				if alert.state != Triggered_alarm.ACTIVE:
					x = reduce(lambda x,y: x if x['date']>y['date'] else y, alert.value.values('date'))
					end_date = x["date"]

				alert_types = list(set([sub.sensor.sensor_type for sub in alert.alarm.subscriptions.all()]))
				sens = list(set([sub.sensor for sub in alert.alarm.subscriptions.all()]))
				alerts_dict += [{"id":alert.id, "alert_id":alert.alarm.id, "name":alert.alarm.name, "state":dict(Triggered_alarm.STATE_CHOICES)[alert.state],  "start_date":value.date, "end_date":end_date, "peak":peak, "peak_date":peak_date, "types":alert_types, 'sens':sens}]

				if alert.alarm.type_alarm != None:
					alerts_dict[-1]["maximum_minimum"] = dict(Alarm.ALARM_CHOICES)[alert.alarm.type_alarm]
					alerts_dict[-1]["threshold"] = alert.alarm.threshold

		form = AlarmForm(subscriptions=not_sender)
		actform = ActuatorForm(senders=senders)

	if request.method == 'POST':
		form = AlarmForm(request.POST)

		if form.is_valid():
			try:
				save_form(form, request.user)
			except Exception as e:
				print e
				return HttpResponseRedirect('/alerts/success='+str(False))
			
			return HttpResponseRedirect('/alerts/success='+str(True))
		
		else:
			return HttpResponseRedirect('/alerts/success='+str(False))

	# Sort alerts by start date
	alerts_dict = sorted(alerts_dict, key=lambda d: d['start_date'], reverse=True)

	return render(request, 'adminlte/alerts.html', {"triggered_alerts":alerts_dict, "success":success, "alerts":alerts, "id":id, "form":form, "actform":actform, "sensors":sensors, "user_types":get_types(request)})

@login_required(login_url="login")
def alert_details(request, id, success=None):
	subscriptions = []
	type_alarm = '-'
	threshold = '-'
	sensors = {}
	triggered_alerts = []
	senders = []
	trig_days = {}

	try:
		alert = Alarm.objects.get(id=id)
	except Exception as e:
		raise Http404

	if request.method=='GET':
		

		# Get the allowed subscriptions
		all_subs = get_subscriptions(request.user)

		name_subs = [{"sub":su.name, "sensor":su.sensor.name, "id":su.subscription_id} for su in alert.subscriptions.all()]
		type_sen = list(set([dict(Sensor.TYPE_CHOICES)[su.sensor.sensor_type] for su in alert.subscriptions.all()]))

		for s in all_subs:
			if not s.sender:
				senders += [(s.subscription_id, s.name)]

		daysWeek = 'All week' if alert.daysOfWeek.count()==7 or alert.daysOfWeek.count()==0 else ", ".join([ str(dict(day_week.DAYS_OF_WEEK)[day]) for day in alert.daysOfWeek.all().values_list('day', flat=True)])

		if alert.type_alarm!=None:
			type_alarm = dict(alert.ALARM_CHOICES)[alert.type_alarm]

		if alert.threshold!=None:
			threshold = alert.threshold

		triggered_alerts += Triggered_alarm.objects.filter(alarm=alert, alarm__user=request.user)

		alerts_dict = []

		for a in triggered_alerts:
			if a.id not in [tmp["id"] for tmp in alerts_dict]:

				all_values = a.value.all()
				all_streams = list(set([value.subscription for value in all_values]))

				for stream in all_streams:
					value = a.value.filter(subscription=stream).earliest('date')

					end_date = "-"
					peak = None
					peak_date = None
					beg_date = x = reduce(lambda x,y: x if x['date']<y['date'] else y, a.value.filter(subscription=stream).values('date'))['date']
					
					if a.alarm.type_alarm==Alarm.MAX:
						x = reduce(lambda x,y: x if float(x['data'])>float(y['data']) else y, a.value.filter(subscription=stream).values('data','date'))
						peak = round(x['data'],2)
						peak_date = x['date']
					elif a.alarm.type_alarm==Alarm.MIN:
						x = reduce(lambda x,y: x if float(x['data'])<float(y['data']) else y, a.value.filter(subscription=stream).values('data'))
						peak = round(x['data'],2)
						peak_date = x['date']

					if a.state != Triggered_alarm.ACTIVE:
						x = reduce(lambda x,y: x if x['date']>y['date'] else y, a.value.filter(subscription=stream).values('date'))
						end_date = x["date"]
				
					alerts_dict += [{"stream": stream, "id":a.id, "name":a.alarm.name, "state":dict(Triggered_alarm.STATE_CHOICES)[a.state],  "start_date":value.date, "end_date":end_date, "peak":peak, "peak_date":peak_date, "beg_date":beg_date}]

					if a.alarm.type_alarm != None:
						alerts_dict[-1]["maximum_minimum"] = dict(Alarm.ALARM_CHOICES)[a.alarm.type_alarm]
						alerts_dict[-1]["threshold"] = a.alarm.threshold

					if beg_date.strftime('%Y/%m/%d') not in trig_days:
						trig_days[beg_date.strftime('%Y/%m/%d')] = 1
					else:
						trig_days[beg_date.strftime('%Y/%m/%d')] += 1

		# Sort alerts by start date
		alerts_dict = sorted(alerts_dict, key=lambda d: d['start_date'], reverse=True)

		actuators = AlarmActuator.objects.filter(alarm=alert)
		act_list = []
		for act in actuators:
			for a in act.subscriptions.all():
				act_list += [{"id":act.id, "value": act.value, "sub":a.name, "sen_name": a.sensor, "sub_id":a.subscription_id}]

		actform = ActuatorForm(senders=senders)
		trig_days = collections.OrderedDict(sorted(trig_days.items()))

	if request.method == 'POST':
		form = ActuatorForm(request.POST)

		if form.is_valid():

			try:
				aa = AlarmActuator(value=form.cleaned_data["value"], alarm=alert)
				aa.save()
				for s in form.cleaned_data["streams"]:
					aa.subscriptions.add(Subscription.objects.get(subscription_id=s))
			except Exception as e:
				return HttpResponseRedirect('/alerts/details/'+id+'/success='+str(False)+'actuator')

			
			return HttpResponseRedirect('/alerts/details/'+id+'/success='+str(True)+'actuator')

		else:
			return HttpResponseRedirect('/alerts/details/'+id+'/success='+str(False)+'actuator')


	return render(request, 'adminlte/alert_details.html', {"user_types":get_types(request), 'subscription_sensor':name_subs, 'name': alert.name, 'type': type_alarm, 'HasThreshold': alert.has_threshold, 'threshold': threshold, 'id': alert.id, 
				'beg_date':alert.beg_date, 'end_date':alert.end_date, 'daysOfWeek':daysWeek, 'hours_act':alert.hours_active_beg, 'hours_end':alert.hours_active_end, 'state': alert.state, 'date_created': alert.date_created,
				'sen_type':type_sen, 'actuators':act_list, 'triggered_alerts':alerts_dict, "actform":actform, "success":success, "trig_days":json.dumps(trig_days)})

@login_required(login_url="login")
def rules(request, success=None, id=-1):

	subscriptions = []
	alerts = []
	senders = []
	triggeredNotSeen_alerts = []
	triggeredActive_alerts = []
	all_alerts = []
	sensors = []

	if request.method=='GET':
		
		# Get the allowed subscriptions
		all_subs = get_subscriptions(request.user)

		# Check if all actuators are allowed for the user
		aa = AlarmActuator.objects.filter(alarm__state=Alarm.ACTIVE, alarm__has_threshold=False, alarm__user=request.user)

		for a in aa:
			done = True
			for entry in a.subscriptions.all():
				if entry not in all_subs:
					done = False
			if done and a.alarm not in all_alerts:
				all_alerts += [a.alarm]

		for s in all_subs:
			if not s.sender:
				senders += [(s.subscription_id, s.name)]

		for alert in all_alerts:

			name_subs = [su.name for su in alert.subscriptions.all()]
			daysWeek = 'All week' if alert.daysOfWeek.count()==7 or alert.daysOfWeek.count()==0 else ", ".join([ str(dict(day_week.DAYS_OF_WEEK)[day]) for day in alert.daysOfWeek.all().values_list('day', flat=True)])

			if alert.id not in [al["id"] for al in alerts]:
				alert_types = list(set([sub.sensor.sensor_type for a in aa for sub in a.subscriptions.all()]))
				sens = list(set([sub.sensor for a in aa for sub in a.subscriptions.all()]))
				alerts += [{"id":alert.id, 'subscription_name':", ".join(name_subs), 'name':alert.name, 'beg_date':alert.beg_date, 'end_date':alert.end_date, 'daysOfWeek':daysWeek, 'hours_act':alert.hours_active_beg, 'hours_beg':alert.hours_active_end, 'state': alert.state, 'types':alert_types, 'sens':sens}]
				
		form = RuleForm(senders=senders)
		actform = ActuatorForm(senders=senders)

	if request.method == 'POST':
		form = RuleForm(request.POST)

		if form.is_valid():
			try:
				save_rule(form, request.user)
			except Exception as e:
				print e
				return HttpResponseRedirect('/rules/success='+str(False))
			
			return HttpResponseRedirect('/rules/success='+str(True))
		
		else:
			return HttpResponseRedirect('/rules/success='+str(False))

	return render(request, 'adminlte/rules.html', {"user_types":get_types(request), "rules":alerts, "success":success, "form":form, "actform":actform})

@login_required(login_url="login")
def rule_details(request, id, success=None):
	actuators = []

	try:
		alert = Alarm.objects.get(id=id)
	except Exception as e:
		raise Http404

	if request.method=='GET':

		# Get the allowed subscriptions
		all_subs = get_subscriptions(request.user)

		senders = [(s.subscription_id, s.name) for s in all_subs if not s.sender]
		
		name = alert.name

		aa = AlarmActuator.objects.filter(alarm=alert)

		all_subs = [sub for a in aa for sub in a.subscriptions.all()]
		types = list(set([dict(Sensor.TYPE_CHOICES)[a.sensor.sensor_type] for a in all_subs]))

		beg_date = alert.beg_date
		end_date = alert.end_date
		
		daysWeek = 'All week' if alert.daysOfWeek.count()==7 or alert.daysOfWeek.count()==0 else ", ".join([ str(dict(day_week.DAYS_OF_WEEK)[day]) for day in alert.daysOfWeek.all().values_list('day', flat=True)])

		trigger = alert.hours_active_beg
		

		act_list = []
		for act in aa:
			for a in act.subscriptions.all():
				act_list += [{"id":act.id, "value": act.value, "sub":a.name, "sen_name": a.sensor, "sub_id":a.subscription_id}]

		actform = ActuatorForm(senders=senders)

	if request.method == 'POST':
		form = ActuatorForm(request.POST)

		if form.is_valid():

			try:
				aa = AlarmActuator(value=form.cleaned_data["value"], alarm=alert)
				aa.save()
				for s in form.cleaned_data["streams"]:
					aa.subscriptions.add(Subscription.objects.get(subscription_id=s))
			except Exception as e:
				return HttpResponseRedirect('/rules/details/'+id+'/success='+str(False)+'actuator')

			
			return HttpResponseRedirect('/rules/details/'+id+'/success='+str(True)+'actuator')

		else:
			return HttpResponseRedirect('/rules/details/'+id+'/success='+str(False)+'actuator')

	return render(request, 'adminlte/rule_details.html', {"user_types":get_types(request), "name":name, "sen_type":types, "beg_date":beg_date, "end_date":end_date, "daysOfWeek":daysWeek, "hours_act":trigger, "actuators":act_list, "actform":actform, "success":success})

@login_required(login_url="login")
def help(request):
	return render(request, 'adminlte/help.html', {"user_types":get_types(request)})

@login_required(login_url="login")
def details(request, s_id, success=None):

	sensor = []
	subscriptions = []
	working = 0
	not_working = 0
	values = {}
	alerts = []
	sensor_subscriptions = []
	triggered_alerts = []
	rules = []
	all_alerts = []
	senders = []
	reports_dict = []
	reports_day = {}
	senders2 = []
	not_sender = []
	has_senders = False

	try:
		sensor = Sensor.objects.get(device_id=str(s_id))
	except Exception as e:
		raise Http404

	if request.method == 'GET':

		# Get the allowed subscriptions
		all_subs = get_subscriptions(request.user)
		
		#### Get all the rules
		# Check if all actuators are allowed for the user
		aa = AlarmActuator.objects.filter(alarm__state=Alarm.ACTIVE, alarm__has_threshold=False, alarm__user=request.user)

		for a in aa:
			done = True
			is_this_sensor = False
			for entry in a.subscriptions.all():
				if entry not in all_subs:
					done = False
				if entry.sensor.device_id==sensor.device_id:
					is_this_sensor = True
			if done and is_this_sensor and a.alarm not in all_alerts:
				all_alerts += [a.alarm]

		for rule in all_alerts:

			name_subs = list(set([sub.name for a in aa for sub in a.subscriptions.all()]))
			daysWeek = 'All week' if rule.daysOfWeek.count()==7 or rule.daysOfWeek.count()==0 else ", ".join([ str(dict(day_week.DAYS_OF_WEEK)[day]) for day in rule.daysOfWeek.all().values_list('day', flat=True)])

			if rule.id not in [al["id"] for al in rules]:
				rule_types = list(set([sub.sensor.sensor_type for a in aa for sub in a.subscriptions.all()]))
				sen_name = list(set([sub.sensor.name for a in aa for sub in a.subscriptions.all()]))
				sen_id = list(set([sub.sensor.device_id for a in aa for sub in a.subscriptions.all()]))
				rules += [{"id":rule.id, 'subscription_name':", ".join(name_subs), 'name':rule.name, 'beg_date':rule.beg_date, 'end_date':rule.end_date, 'daysOfWeek':daysWeek, 'hours_act':rule.hours_active_beg, 'hours_beg':rule.hours_active_end, 'state': rule.state, 'types':rule_types, 'sen_name': ", " .join(sen_name), 'sen_id':", " .join(sen_id)}]
		####
		
		for subsc in all_subs:
			
			if not subsc.sender:
				senders += [(subsc.subscription_id, subsc.name)]
			
			if subsc.sensor.device_id == sensor.device_id:

				if not subsc.sender:
					has_senders = True
					senders2 += [(subsc.subscription_id, subsc.name)]
				else:
					not_sender += [(subsc.subscription_id, subsc.name)]
				subscriptions +=  (subsc.subscription_id, subsc.name),
				sensor_subscriptions += [{"id":subsc.subscription_id, "name":subsc.name, "date":subsc.date_added, "working":subsc.working, "subtype":subsc.subtype, "sender":not subsc.sender}]
				
				
				# All the User Reports associated to the subscription ordered by date
				reports = UserReport.objects.filter(deleted=False, subscription=subsc).order_by('-date')
				for report in reports:
					reports_dict += [{"id":report.id, "state":dict(UserReport.TYPE_CHOICES)[report.state], "working_state":dict(UserReport.WORKING_CHOICES)[report.working_state], "information":report.information, "date":report.date, "stream":report.subscription.name, "email":report.email, "title":report.title, "name": report.user_name, "sen_name":report.subscription.sensor.name, "sen_type":report.subscription.sensor.sensor_type }]
					
					if report.date.date().strftime('%Y/%m/%d') not in reports_day:
						reports_day[report.date.date().strftime('%Y/%m/%d')] = 1
					else:
						reports_day[report.date.date().strftime('%Y/%m/%d')] += 1


				if subsc.working:
					working += 1
				else:
					not_working += 1

				v = Value.objects.filter(subscription_id=subsc.subscription_id).values("date", "data")
				
				if v:
					if subsc.subtype.name not in values:
						values[subsc.subtype.name] = json.dumps({subsc.name:[[[s['date'].year, s['date'].month, s['date'].day, s['date'].hour, s['date'].minute], s['data']] for s in v]})
					else:
						values[subsc.subtype.name] += json.dumps({subsc.name:[[[s['date'].year, s['date'].month, s['date'].day, s['date'].hour, s['date'].minute], s['data']] for s in v]})
					
				for alert in Alarm.objects.filter(subscriptions=subsc.subscription_id, user=request.user, has_threshold=True):
					if (alert.state==Alarm.ACTIVE):
						if alert.id not in [al["id"] for al in alerts]:
							name_subs = [su.name for su in alert.subscriptions.all()]
							daysWeek = 'All week' if alert.daysOfWeek.count()==7 or alert.daysOfWeek.count()==0 else ", ".join([ str(dict(day_week.DAYS_OF_WEEK)[day]) for day in alert.daysOfWeek.all().values_list('day', flat=True)])
							alerts += [{"id":alert.id, 'subscription_name':", ".join(name_subs), 'name':alert.name, 'beg_date':alert.beg_date, 'end_date':alert.end_date, 'daysOfWeek':daysWeek, 'hours_act':alert.hours_active_beg, 'hours_beg':alert.hours_active_end}]
							if alert.type_alarm!=None:
								alerts[-1]['type_alarm'] = dict(alert.ALARM_CHOICES)[alert.type_alarm]

							if alert.threshold!=None:
								alerts[-1]['threshold'] = alert.threshold

					tas = Triggered_alarm.objects.filter(alarm=alert, deleted=False)
					
					for ta in tas:
						if ta.id not in [al["id"] for al in triggered_alerts]:

							value = ta.value.earliest('date')

							end_date = "-"
							peak = "-"
							peak_date = "-"

							if ta.alarm.type_alarm==Alarm.MAX:

								x = reduce(lambda x,y: x if float(x['data'])>float(y['data']) else y, ta.value.values('data','date'))
								peak = round(x['data'],2)
								peak_date = x['date']
							elif ta.alarm.type_alarm==Alarm.MIN:
								x = reduce(lambda x,y: x if float(x['data'])<float(y['data']) else y, ta.value.values('data','date'))
								peak = round(x['data'],2)
								peak_date = x['date']

							if ta.state != Triggered_alarm.ACTIVE:
								x = reduce(lambda x,y: x if x['date']>y['date'] else y, ta.value.values('date'))
								end_date = x["date"]

							alert_types = list(set([sub.sensor.sensor_type for sub in ta.alarm.subscriptions.all()]))
							
							triggered_alerts += [{"id":ta.id, "alert_id":alert.id, "name":alert.name, "state":dict(Triggered_alarm.STATE_CHOICES)[ta.state],"start_date":value.date,"end_date":end_date, "peak":peak, "peak_date":peak_date, "types":alert_types}]
							
							if alert.type_alarm!=None:
								triggered_alerts[-1]['maximum_minimum'] = dict(alert.ALARM_CHOICES)[alert.type_alarm]

							if alert.threshold!=None:
								triggered_alerts[-1]['threshold'] = alert.threshold

		rule_form = RuleForm(senders=senders)
		form = AlarmForm(subscriptions=not_sender)

		actform = ActuatorForm(senders=senders)
		actform2 = ActuatorForm(senders=senders2)
		report_days = sorted(reports_day)

	if request.method == 'POST':
		form = AlarmForm(request.POST)

		if form.is_valid():
			try:
				save_form(form, request.user)
			except Exception as e:
				print e
				return HttpResponseRedirect('/sensors/details/'+sensor.device_id+'/success='+str(False))
			
			return HttpResponseRedirect('/sensors/details/'+sensor.device_id+'/success='+str(True))
		
		else:
			return HttpResponseRedirect('/sensors/details/'+sensor.device_id+'/success='+str(False))
		
	json_content = json.dumps(values)

	template = ""

	if sensor.sensor_type==Sensor.TEMPERATURE:
		template = "temperature"

	elif sensor.sensor_type==Sensor.WASTE:
		template = "waste"

	elif sensor.sensor_type==Sensor.PEOPLE:
		template = "people"

	elif sensor.sensor_type==Sensor.NOISE:
		template = "sound"

	elif sensor.sensor_type==Sensor.RADIATION:
		template = "uvradiation"

	elif sensor.sensor_type==Sensor.AIR:
		template = "air"

	elif sensor.sensor_type==Sensor.LIGHTING:
		template = "illumination"

	return render(request, 'adminlte/sensors_' + template + '.html', {"type":dict(Sensor.TYPE_CHOICES)[sensor.sensor_type], "id":sensor.device_id, "name":sensor.name, "information":sensor.information, "lat": Localization.objects.get(pk=sensor.localization.id).lat, "lon": Localization.objects.get(pk=sensor.localization.id).lon, "active":working, "inactive":not_working,
		"value":json_content, "turned_on":sensor.active, "form":form, "ruleform":rule_form, "actform":actform, "alerts":alerts, "success":success, "subscriptions":sensor_subscriptions, "triggered_alerts":triggered_alerts, "reports":reports_dict, "user_types":get_types(request), "address":sensor.localization.address, "report_days":json.dumps(reports_day), "rules":rules, "has_senders":has_senders, "actform2":actform2})

# Add actuator to alert
@login_required()
def add_actuator(request, s_id, success, alertId):

	try:
		sensor = Sensor.objects.get(device_id=str(s_id))
	except Exception as e:
		raise Http404

	try:
		alert = Alarm.objects.get(id=str(alertId))
	except Exception as e:
		raise Http404

	if request.method == 'POST':
		
		form = ActuatorForm(request.POST)

		if form.is_valid():

			try:
				aa = AlarmActuator(value=form.cleaned_data["value"], alarm=alert)
				aa.save()
				for s in form.cleaned_data["streams"]:
					aa.subscriptions.add(Subscription.objects.get(subscription_id=s))
			except Exception as e:
				return HttpResponseRedirect('/sensors/details/'+sensor.device_id+'/success='+str(False)+'actuator')

			
			return HttpResponseRedirect('/sensors/details/'+sensor.device_id+'/success='+str(True)+'actuator')

		else:
			return HttpResponseRedirect('/sensors/details/'+sensor.device_id+'/success='+str(False)+'actuator')

# Add rule to sensor
@login_required()
def add_rule(request, s_id, success):
	
	try:
		sensor = Sensor.objects.get(device_id=str(s_id))
	except Exception as e:
		raise Http404


	if request.method == 'POST':
		
		form = RuleForm(request.POST)

		if form.is_valid():
			try:
				save_rule(form, request.user)
			
			except Exception as e:
				print e
				return HttpResponseRedirect('/sensors/details/'+sensor.device_id+'/success='+str(False)+'Rule')

			
			return HttpResponseRedirect('/sensors/details/'+sensor.device_id+'/success='+str(True)+'Rule')

		else:
			return HttpResponseRedirect('/sensors/details/'+sensor.device_id+'/success='+str(False)+'Rule')


# Add actuator to alert
@login_required()
def add_actuator2(request, alertId):
	
	try:
		alert = Alarm.objects.get(id=str(alertId))
	except Exception as e:
		raise Http404

	if request.method == 'POST':
		
		form = ActuatorForm(request.POST)

		if form.is_valid():

			try:
				aa = AlarmActuator(value=form.cleaned_data["value"], alarm=alert)
				aa.save()
				for s in form.cleaned_data["streams"]:
					aa.subscriptions.add(Subscription.objects.get(subscription_id=s))
			except Exception as e:
				return HttpResponseRedirect('/alerts/success='+str(False)+'actuator')

			
			return HttpResponseRedirect('/alerts/success='+str(True)+'actuator')

		else:
			return HttpResponseRedirect('/alerts/success='+str(False)+'actuator')

# Add actuator to alert
@login_required()
def addActuatorToRule(request, s_id):
	
	try:
		alert = Alarm.objects.get(id=str(s_id))
	except Exception as e:
		raise Http404

	if request.method == 'POST':
		
		form = ActuatorForm(request.POST)

		if form.is_valid():

			try:
				aa = AlarmActuator(value=form.cleaned_data["value"], alarm=alert)
				aa.save()
				for s in form.cleaned_data["streams"]:
					aa.subscriptions.add(Subscription.objects.get(subscription_id=s))
			except Exception as e:
				return HttpResponseRedirect('/rules/success='+str(False)+'actuator')

			
			return HttpResponseRedirect('/rules/success='+str(True)+'actuator')

		else:
			return HttpResponseRedirect('/rules/success='+str(False)+'actuator')




# Add actuator to page alert
@login_required()
def add_actuator_alert(request, s_id, success, alertId):
	
	try:
		sensor = Sensor.objects.get(device_id=str(s_id))
	except Exception as e:
		raise Http404

	try:
		alert = Alarm.objects.get(id=str(alertId))
	except Exception as e:
		raise Http404

	if request.method == 'POST':
		
		form = ActuatorForm(request.POST)

		if form.is_valid():

			try:
				aa = AlarmActuator(value=form.cleaned_data["value"], alarm=alert)
				aa.save()
				for s in form.cleaned_data["streams"]:
					aa.subscriptions.add(Subscription.objects.get(subscription_id=s))
			except Exception as e:
				return HttpResponseRedirect('/alerts/'+sensor.device_id+'/success='+str(False)+'actuator')

			
			return HttpResponseRedirect('/alerts/'+sensor.device_id+'/success='+str(True)+'actuator')

		else:
			return HttpResponseRedirect('/alerts/'+sensor.device_id+'/success='+str(False)+'actuator')


# API for changing the state of a sensor
@login_required()
def change_sensor(request, state, sensor):

	if request.method == 'POST':
		try:
			sensor = Sensor.objects.get(device_id=sensor)
		except Exception as e:
			return JsonResponse({'status':'Error', 'info': 'Could not find sensor'})


		if state == 'on':
			if sensor.active == True:
				return JsonResponse({'status':'Error', 'info':'Sensor was already turned on'})
			else:
				sensor.active = True
				sensor.save()
				return JsonResponse({'status':'Success', 'info':'Sensor successfully turned on'})

		elif state == 'off':
			if sensor.active == False:
				return JsonResponse({'status':'Error', 'info':'Sensor was already turned off'})
			else:
				sensor.active = False
				sensor.save()
				return JsonResponse({'status':'Success', 'info': 'Sensor successfully turned off'})

		else:
			return JsonResponse({'status':'Error', 'info': 'Invalid sensor state'})


		return JsonResponse({'status':'Error', 'info': 'Could not find sensor'})
	else:
		raise Http404

# API to delete note
@login_required()
def delete_note(request, id):
	if request.method == 'POST':
		try:
			note = Note.objects.get(id=id)
		except Exception as e:
			return JsonResponse({'status':'Error', 'info': 'Could not find note'})

		if note.state == Note.INACTIVE:
			return JsonResponse({'status':'Error', 'info':'Note was already deleted'})
		else:
			note.state = Note.INACTIVE
			note.save()
			return JsonResponse({'status':'Success', 'info': 'Note successfully deleted'})

	else:
		raise Http404

# API to return information about a note
@login_required()
def info_note(request, id):
	try:
		note = Note.objects.get(id=id)
	except Exception as e:
		return JsonResponse({'status':'Error', 'info': 'Could not find note'})

	return JsonResponse({'status':'OK', 'name': note.name, 'date_beg':note.date_beginning, 'date_end':note.date_end,'info':note.information})

# API to add note
@login_required()
def add_note(request):
	if request.method == 'POST':
		form = NoteForm(request.POST)

		if form.is_valid():
			try:
				save_note_form(form, request.user)
			except Exception as e:
				return HttpResponseRedirect('../success='+str(False))
			
			return HttpResponseRedirect('../success='+str(True))
		
		else:
			return HttpResponseRedirect('../success='+str(False))

# API to change state of report
@login_required()
def change_state_report(request, id, state):
	if request.method == 'POST':
		try:
			report = UserReport.objects.get(id=id)
		except Exception as e:
			return JsonResponse({'status':'Error', 'info': 'Could not find Report'})

		if report.state==state:
			return JsonResponse({'status':'Error', 'info': 'Report already on the desired state'})

		if state=='NS':
			report.state = UserReport.NOT_SEEN
		elif state=='SE':
			report.state = UserReport.SEEN
		else:
			return JsonResponse({'status':'Error', 'info': 'Report state does not exist'})

		report.save()

		return JsonResponse({'status':'Success', 'info': 'Report succesfully changed state'})

# API to delete report
@login_required()
def delete_report(request, id):
	if request.method == 'POST':
		try:
			report = UserReport.objects.get(id=id)
		except Exception as e:
			return JsonResponse({'status':'Error', 'info': 'Could not find Report'})

		report.deleted = True
		report.save()

		return JsonResponse({'status':'Success', 'info': 'Report succesfully deleted'})

# API to change state of report
@login_required()
def change_working_state_report(request, id, state):
	if request.method == 'POST':
		try:
			report = UserReport.objects.get(id=id)
		except Exception as e:
			return JsonResponse({'status':'Error', 'info': 'Could not find Report'})

		if report.state==state:
			return JsonResponse({'status':'Error', 'info': 'Report already on the desired state'})

		if state=='WA':
			report.working_state = UserReport.WAITING
		elif state=='WI':
			report.working_state = UserReport.WORKING_ON_IT
		elif state=='SO':
			report.working_state = UserReport.SOLVED
		else:
			return JsonResponse({'status':'Error', 'info': 'Report state does not exist'})

		report.save()

		return JsonResponse({'status':'Success', 'info': 'Report succesfully changed state'})



# API to change state of triggered alert
@csrf_exempt
def change_state_TrigAlert(request, id, state):
	if request.method == 'POST':
		try:
			alert = Triggered_alarm.objects.get(id=id)
		except Exception as e:
			return JsonResponse({'status':'Error', 'info': 'Could not find alarm'})

		if state=='AC':
			alert.state = Triggered_alarm.ACTIVE
		elif state=='NS':
			alert.state = Triggered_alarm.NOT_SEEN
		elif state=='SE':
			alert.state = Triggered_alarm.SEEN
		else:
			return JsonResponse({'status':'Error', 'info': 'Alarm state does not exist'})

		alert.save()

		return JsonResponse({'status':'Success', 'info': 'Alarm succesfully changed state'})

# API to change state of alarm to deleted
@login_required()
def delete_alert(request, id):
	if request.method == 'POST':
		try:
			alert = Alarm.objects.get(id=id)
		except Exception as e:
			return JsonResponse({'status':'Error', 'info': 'Could not find alarm'})


	# Change the state of all triggered alarms from active to not seen
	t_alerts = Triggered_alarm.objects.filter(alarm=alert)
	for t in t_alerts:
		if t.state==Triggered_alarm.ACTIVE:
			t.state = Triggered_alarm.NOT_SEEN
			t.save()


	alert.state = Alarm.DELETED

	alert.save()

	return JsonResponse({'status':'Success', 'info': 'Alarm succesfully deleted'})

def deleteStreamFromAlert(request, id, sub):
	if request.method == 'POST':
		try:
			alert = Alarm.objects.get(id=id)
		except Exception as e:
			return JsonResponse({'status':'Error', 'info': 'Could not find alarm'})

	try:

		sub = Subscription.objects.get(subscription_id=sub)
	except Exception as e:
		return JsonResponse({'status': 'Error', 'info': "The subscription could not be found"})

	try:
		alert.subscriptions.remove(sub)
	except Exception as e:
		return JsonResponse({'status': 'Error', 'info': "The subscription is not associated with the alert"})


	if len(alert.subscriptions.all())==0:
		alert.state = Alarm.DELETED

	return JsonResponse({'status':'Success', 'info': 'Stream succesfully deleted'})


#API to delete triggered alert
@login_required()
def delete_TrigAlert(request, id):
	if request.method == 'POST':
		try:
			alert = Triggered_alarm.objects.get(id=id)
		except Exception as e:
			return JsonResponse({'status':'Error', 'info':'Could not find triggered alert'})

		alert.deleted = True

		alert.save()
		return JsonResponse({'status':'Success', 'info': 'Triggered alert succesfully deleted'})

#API to delete triggered alert
@login_required()
def deleteTrigAlert(request, id, sen):
	if request.method == 'POST':
		try:
			alert = Triggered_alarm.objects.get(id=id)
		except Exception as e:
			return JsonResponse({'status':'Error', 'info':'Could not find triggered alert'})

		try:
			sensor = Sensor.objects.get(device_id=sen)
		except Exception as e:
			return JsonResponse({'status':'Error', 'info':'Could not find sensor'})

		values = [value for value in alert.value.all() if value.subscription.sensor.device_id==sensor.device_id]
		

		for value in values:
			alert.value.remove(value)

		if len(alert.value.all())==0:
			alert.deleted = True

		alert.save()
		return JsonResponse({'status':'Success', 'info': 'Triggered alert succesfully deleted'})

#API to return information about a active alert
def info_alert(request, id):
	subscriptions = []
	active_alerts = []
	type_alarm = '-'
	threshold = '-'

	if request.method=='GET':
		try:
			alert = Alarm.objects.get(id=id)
		except Exception as e:
			return JsonResponse({'status':'Error', 'info': 'Could not find Alarm'})


		name_subs = len([su.name for su in alert.subscriptions.all()])
		name_sensors = len(list(set([su.sensor.name for su in alert.subscriptions.all()])))
		type_sen = list(set([dict(Sensor.TYPE_CHOICES)[su.sensor.sensor_type] for su in alert.subscriptions.all()]))


		daysWeek = 'All week' if alert.daysOfWeek.count()==7 or alert.daysOfWeek.count()==0 else ", ".join([ str(dict(day_week.DAYS_OF_WEEK)[day]) for day in alert.daysOfWeek.all().values_list('day', flat=True)])

		if alert.type_alarm!=None:
			type_alarm = dict(alert.ALARM_CHOICES)[alert.type_alarm]

		if alert.threshold!=None:
			threshold = alert.threshold

		actuators = len(AlarmActuator.objects.filter(alarm=alert))

		return JsonResponse({'status':'OK', 'subscription_name': name_subs, 'name': alert.name, 'type': type_alarm, 'HasThreshold': alert.has_threshold, 'threshold': threshold, 'id': alert.id, 
				'beg_date':alert.beg_date, 'end_date':alert.end_date, 'daysOfWeek':daysWeek, 'hours_act':alert.hours_active_beg, 'hours_end':alert.hours_active_end, 'state': alert.state, 'date_created': alert.date_created, 'sen_name':name_sensors, 'sen_type':type_sen, 'actuators':actuators})

#API to return information about a triggered alert
def info_triggered(request, id):
	threshold = '-'
	maximum_minimum = '-'

	try:
		alarm = Triggered_alarm.objects.get(id=id)
	except Exception as e:
		return JsonResponse({'status':'Error', 'info': 'Could not find Triggered Alarm'})
	
	
	end_date = "-"
	peak = "-"
	peak_date = "-"
	sub_name = []
	sen_name = []
	sen_type = []

	for v in alarm.value.all():

		if v.subscription.name not in sub_name:
			sub_name += [v.subscription.name]

		if v.subscription.sensor.name not in sen_name:
			sen_name += [v.subscription.sensor.name]

		if dict(Sensor.TYPE_CHOICES)[v.subscription.sensor.sensor_type] not in sen_type:
			sen_type += [dict(Sensor.TYPE_CHOICES)[v.subscription.sensor.sensor_type]]


	value = alarm.value.earliest('date')

	if alarm.alarm.type_alarm==Alarm.MAX:
		x = reduce(lambda x,y: x if float(x['data'])>float(y['data']) else y, alarm.value.values('data','date'))
		peak = round(x['data'],2)
		peak_date = x['date']
	elif alarm.alarm.type_alarm==Alarm.MIN:
		x = reduce(lambda x,y: x if float(x['data'])<float(y['data']) else y, alarm.value.values('data','date'))
		peak = round(x['data'],2)
		peak_date = x['date']

	if alarm.state != Triggered_alarm.ACTIVE:
		x = reduce(lambda x,y: x if x['date']>y['date'] else y, alarm.value.values('date'))
		end_date = x["date"]

	
	if alarm.alarm.type_alarm != None:
		maximum_minimum = dict(Alarm.ALARM_CHOICES)[alarm.alarm.type_alarm]
		threshold = alarm.alarm.threshold

	daysWeek = 'All week' if alarm.alarm.daysOfWeek.count()==7 or alarm.alarm.daysOfWeek.count()==0 else ", ".join([ str(dict(day_week.DAYS_OF_WEEK)[day]) for day in alarm.alarm.daysOfWeek.all().values_list('day', flat=True)])

	return JsonResponse({'status':'OK', 'name': alarm.alarm.name, 'threshold':threshold, 'types': maximum_minimum, 'start_date':value.date, 'end_date': end_date, 'peak':peak, 'peak_date':peak_date, 
		'state':dict(Triggered_alarm.STATE_CHOICES)[alarm.state], 'has_threshold':alarm.alarm.has_threshold, 'dateCreated': alarm.alarm.date_created, 'daysWeek': daysWeek, 'hours_act':alarm.alarm.hours_active_beg, 'hours_end': alarm.alarm.hours_active_end, 'sub_name':sub_name, 'sen_name':sen_name, 'SenType':sen_type})

# API to send all alerts to mobile user
def info_trigalerts(request):
	alerts_dict = []
	if request.method=='GET':
		
		subscriptions_allowed = get_mobile_subscriptions()
		
		for s in subscriptions_allowed:
			for a in Alarm.objects.filter(subscriptions=s.subscription_id, state=Alarm.ACTIVE, has_threshold=True):
				triggered_alarms = Triggered_alarm.objects.filter(Q(alarm=a) & Q(deleted=False) & (Q(state=Triggered_alarm.NOT_SEEN) | Q(state=Triggered_alarm.ACTIVE)))
				
				if len(triggered_alarms)>0:
					for triggered in triggered_alarms:
						value = triggered.value.earliest('date')

						end_date = "-"
						peak = None
						peak_date = None

						
						if triggered.alarm.type_alarm==Alarm.MAX:
							x = reduce(lambda x,y: x if float(x['data'])>float(y['data']) else y, triggered.value.values('data','date'))
							peak = round(x['data'],2)
							peak_date = x['date']
						elif triggered.alarm.type_alarm==Alarm.MIN:
							x = reduce(lambda x,y: x if float(x['data'])<float(y['data']) else y, triggered.value.values('data','date'))
							peak = round(x['data'],2)
							peak_date = x['date']

						if triggered.state != Triggered_alarm.ACTIVE:
							x = reduce(lambda x,y: x if x['date']>y['date'] else y, triggered.value.values('date'))
							end_date = x["date"]

						alert_types = list(set([sub.sensor.sensor_type for sub in triggered.alarm.subscriptions.all()]))
						sens = list(set([sub.sensor.name for sub in triggered.alarm.subscriptions.all()]))

						if triggered.id not in [al["id"] for al in alerts_dict]:
							alerts_dict += [{"id":triggered.id, "alert_id":triggered.alarm.id, "name":triggered.alarm.name, "state":dict(Triggered_alarm.STATE_CHOICES)[triggered.state], "start_date":value.date, "end_date":end_date, "peak":peak, "peak_date":peak_date, "types of sensors":alert_types, "sensors":sens}]

						if triggered.alarm.type_alarm != None:
							alerts_dict[-1]["maximum_minimum"] = dict(Alarm.ALARM_CHOICES)[triggered.alarm.type_alarm]
							alerts_dict[-1]["threshold"] = triggered.alarm.threshold

		return JsonResponse({'status':'OK', 'occurrences': alerts_dict})

# API to send value to actuator
@login_required()
def send_value(request, id, value):
	sub = []

	if request.method == 'POST':
		try:
			sub = Subscription.objects.get(subscription_id=id)
		except Exception as e:
			return JsonResponse({'status':'Error', 'info': 'Could not find stream'})

		try:
			value = float(value)
		except Exception as e:
			return JsonResponse({'status':'Error', 'info': 'Value sent is not on the desired format (decimal)'})

		sensor_id = sub.sensor.device_id;
		#tasks.receive_data()

		resp = tasks.send_data(sensor_id, sub.name, value)
		if resp[0]!=202:
			return JsonResponse({'status':'Error', 'info': 'Could not communicate with the platform'})

		v = Value(data=value, timeToLive=3600, date=datetime.datetime.now().isoformat(), subscription=sub)
		v.save()

		return JsonResponse({'status':'Success', 'info': 'Value successfully sent to the actuator'})


# API to dynamically add a new sensor
@csrf_exempt
def add_sensor(request):
	if request.method == 'POST':
		try:
			received_json_data=json.loads(request.body)
			device_id = received_json_data['id']
			device_password = received_json_data['password']
			device_name = received_json_data['name']
			device_description = received_json_data['description']
			device_type = received_json_data['type']
			device_lat = received_json_data['lat']
			device_lon = received_json_data['lon']
		except Exception as e:
			return JsonResponse({'status': 'Error', 'info': 'Wrong parameters send in request body.'})
		try:
			t = tasks.reg_device(device_id, device_password, device_name, device_description, device_type, device_lat, device_lon)
		except Exception as e:
			print e
			return JsonResponse({'status': 'Error', 'info': 'Could not add sensor'})

		if t!=True:
			return JsonResponse({'status': 'Error', 'info': 'Could not add sensor'})

		return JsonResponse({'status': 'OK', 'info': 'Sensor was successfully added.'})

# API to dynamically add subscription
@csrf_exempt
def add_subscription(request):
	if request.method == 'POST':
		try:
			received_json_data=json.loads(request.body)
			sensor_id = received_json_data["sensor_id"]
			subtype = received_json_data["subtype"]
			subs_name = received_json_data["sub_name"]
			sub_description = received_json_data["sub_description"]
			if "point_of_contact" in received_json_data:
				sub_point_of_contact = received_json_data["point_of_contact"]
			else:
				sub_point_of_contact = None
		except Exception as e:
			return JsonResponse({'status': 'Error', 'info': 'Wrong parameters send in request body.'})
		
		try:
			t = tasks.add_stream(sensor_id, subtype, subs_name, sub_description, sub_point_of_contact)
		except Exception as e:
			print e
			return JsonResponse({'status': 'Error', 'info': 'Could not add stream'})

		if t!=True:
			return JsonResponse({'status': 'Error', 'info': 'Could not add stream'})

		return JsonResponse({'status': 'OK', 'info': 'Stream successfully added.'})

# API to get the number of new sensors
@login_required()
def newSensors(request):
	if request.method=='GET':
		if not request.user.is_staff:
			return JsonResponse({'status': 'Error', 'info': 'User not allowed to see the information'})

		sen = Sensor.objects.filter(state=Sensor.NOT_SEEN)
		for s in sen:
			s.state = Sensor.SEEN
			s.save()
		return JsonResponse({'status': 'Success', 'info': len(sen)})


@login_required()
def delete_actuator(request, id, sub_id):

	if request.method=='POST':
		try:
			actuator = AlarmActuator.objects.get(id=id)
		except Exception as e:
			return JsonResponse({'status': 'Error', 'info': "The actuator does not exist."})

		try:

			sub = Subscription.objects.get(subscription_id=sub_id)
		except Exception as e:
			return JsonResponse({'status': 'Error', 'info': "The subscription could not be found"})


		try:
			actuator.subscriptions.remove(sub)
		except Exception as e:
			return JsonResponse({'status': 'Error', 'info': "The subscription is not associated with the actuator"})


		if actuator.alarm.has_threshold==False and len(actuator.subscriptions.all())==0:
			actuator.delete()

		return JsonResponse({'status': 'Success', 'info': "The actuator was successfully deleted."})

@login_required()
def get_document(request, id_attach):
	if request.method=='GET':
		try:
			attach = ReportAttach.objects.get(id=id_attach)
		except Exception as e:
			print e
			raise Http404

		filename = attach.document.name.split('/')[-1]
		
		name, extension = os.path.splitext(attach.document.name)
		mag = magic.from_file(attach.document.name, mime=True)
		
		response = HttpResponse(attach.document, content_type=mag)

		response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)

		return response

def save_note_form(form, user):

	title = form.cleaned_data['title']
	message = form.cleaned_data['message']

	beg_date = datetime.datetime(year=form.cleaned_data['beg_date'].year, month=form.cleaned_data['beg_date'].month, day=form.cleaned_data['beg_date'].day, hour=form.cleaned_data['hours_beg'], minute=form.cleaned_data['minutes_beg'])
	end_date = datetime.datetime(year=form.cleaned_data['end_date'].year, month=form.cleaned_data['end_date'].month, day=form.cleaned_data['end_date'].day, hour=form.cleaned_data['hours_end'], minute=form.cleaned_data['minutes_end'])

	note = Note(
		name=title,
		state=Note.ACTIVE,
		date_beginning=beg_date,
		date_end=end_date,
		information=message,
		user=user
		)


	note.save()

def save_rule(form, user):
	
	name = form.cleaned_data['name']

	daysOfWeek = []

	if form.cleaned_data['mo']==True:
		daysOfWeek += ['MO']
	if form.cleaned_data['tu']==True:
		daysOfWeek += ['TU']
	if form.cleaned_data['we']==True:
		daysOfWeek += ['WE']
	if form.cleaned_data['th']==True:
		daysOfWeek += ['TH']
	if form.cleaned_data['fr']==True:
		daysOfWeek += ['FR']
	if form.cleaned_data['sa']==True:
		daysOfWeek += ['SA']
	if form.cleaned_data['su']==True:
		daysOfWeek += ['SU']

	beg_date = datetime.datetime(year=form.cleaned_data['beg_date'].year, month=form.cleaned_data['beg_date'].month, day=form.cleaned_data['beg_date'].day, hour=form.cleaned_data['beg_hour'], minute=form.cleaned_data['beg_min'])
	end_date = datetime.datetime(year=form.cleaned_data['end_date'].year, month=form.cleaned_data['end_date'].month, day=form.cleaned_data['end_date'].day, hour=form.cleaned_data['end_hour'], minute=form.cleaned_data['end_min'])
	hours_active_beg = datetime.datetime(year=2017,month=1,day=1,hour=form.cleaned_data['hours_active_beg'], minute=form.cleaned_data['minutes_active_beg']).time()
	

	al = Alarm(
		name=name,
		type_alarm=None,
		threshold=None,
		date_created=datetime.datetime.now(),
		beg_date=beg_date,
		end_date=end_date,
		hours_active_end=(datetime.datetime.combine(datetime.date.today(), hours_active_beg)+timedelta(hours=1)).time(),
		hours_active_beg=hours_active_beg,
		user=user,
		has_threshold=False
	)

	al.save()

	for d in daysOfWeek:
		al.daysOfWeek.add(day_week.objects.get(day=d))

	aa = AlarmActuator(value=form.cleaned_data["value"], alarm=al)

	aa.save()

	for s in form.cleaned_data["streams"]:
		aa.subscriptions.add(Subscription.objects.get(subscription_id=s))


def save_form(form, user):

	subscriptions = [Subscription.objects.get(subscription_id=sub_id) for sub_id in form.cleaned_data['subscriptions']]

	type_alarm = form.cleaned_data['type_alarm']
	threshold = form.cleaned_data['threshold']
	name = form.cleaned_data['name']

	daysOfWeek = []

	if form.cleaned_data['mo']==True:
		daysOfWeek += ['MO']
	if form.cleaned_data['tu']==True:
		daysOfWeek += ['TU']
	if form.cleaned_data['we']==True:
		daysOfWeek += ['WE']
	if form.cleaned_data['th']==True:
		daysOfWeek += ['TH']
	if form.cleaned_data['fr']==True:
		daysOfWeek += ['FR']
	if form.cleaned_data['sa']==True:
		daysOfWeek += ['SA']
	if form.cleaned_data['su']==True:
		daysOfWeek += ['SU']
		
	beg_date = datetime.datetime(year=form.cleaned_data['beg_date'].year, month=form.cleaned_data['beg_date'].month, day=form.cleaned_data['beg_date'].day, hour=form.cleaned_data['beg_hour'], minute=form.cleaned_data['beg_min'])
	end_date = datetime.datetime(year=form.cleaned_data['end_date'].year, month=form.cleaned_data['end_date'].month, day=form.cleaned_data['end_date'].day, hour=form.cleaned_data['end_hour'], minute=form.cleaned_data['end_min'])
	hours_active_beg = datetime.datetime(year=2017,month=1,day=1,hour=form.cleaned_data['hours_active_beg'], minute=form.cleaned_data['minutes_active_beg']).time()
	hours_active_end = datetime.datetime(year=2017,month=1,day=1,hour=form.cleaned_data['hours_active_end'], minute=form.cleaned_data['minutes_active_end']).time()
	
	al = Alarm(
		name=name,
		type_alarm=type_alarm,
		threshold=threshold,
		date_created=datetime.datetime.now(),
		beg_date=beg_date,
		end_date=end_date,
		hours_active_end=hours_active_end,
		hours_active_beg=hours_active_beg,
		user=user,
		has_threshold=True
	)

	al.save()
	for s in subscriptions:
		al.subscriptions.add(s)

	for d in daysOfWeek:
		al.daysOfWeek.add(day_week.objects.get(day=d))


def index_calculations(subscriptions):

	temp_subs = []
	temp_notworking = 0

	air_subs = []
	air_notworking = 0

	waste_subs = []
	waste_notworking = 0

	sound_subs = []
	sound_notworking = 0

	radiation_subs = []
	radiation_notworking = 0

	people_subs = []
	people_notworking = 0

	illumination_subs = []
	illumination_notworking = 0

	# Filter subscriptions by type
	# Get only the working subscriptions, and count the others
	for sub in subscriptions:
		sensor = Sensor.objects.get(name=sub.sensor)
		if sensor.sensor_type==Sensor.TEMPERATURE:
			if sensor.active:
				if sub.working:
					temp_subs += [sub]
				else:
					temp_notworking += 1
		elif sensor.sensor_type==Sensor.AIR:
			if sensor.active:
				if sub.working:
					air_subs += [sub]
				else:
					air_notworking += 1
		elif sensor.sensor_type==Sensor.WASTE:
			if sensor.active:
				if sub.working:
					waste_subs += [sub]
				else:
					waste_notworking += 1
		elif sensor.sensor_type==Sensor.NOISE:
			if sensor.active:
				if sub.working:
					sound_subs += [sub]
				else:
					sound_notworking += 1
		elif sensor.sensor_type==Sensor.PEOPLE:
			if sensor.active:
				if sub.working:
					people_subs += [sub]
				else:
					people_notworking += 1
		elif sensor.sensor_type==Sensor.LIGHTING:
			if sensor.active:
				if sub.working:
					illumination_subs += [sub]
				else:
					illumination_notworking += 1
		elif sensor.sensor_type==Sensor.RADIATION:
			if sensor.active:
				if sub.working:
					radiation_subs += [sub]
				else:
					radiation_notworking += 1

	# Temperature
	temp_values = []
	temp_date = "-"

	

	# Get the last values of subscriptions and the date
	if len(temp_subs) != 0:
		for sub in temp_subs:
			if str(sub.subtype.name) == Sensorsubtype.TEMPERATURE:
				val = Value.objects.filter(subscription=sub.subscription_id)
				if val.exists():
					temp_values += [val.latest('date').data]
					temp_date = val.latest('date').date

	# Waste
	waste_values = []
	waste_date = "-"


	if len(waste_subs) != 0:
		for sub in waste_subs:
			if str(sub.subtype.name) == Sensorsubtype.WASTE_FULLNESS:
				val = Value.objects.filter(subscription=sub.subscription_id)
				if val.exists():
					waste_values += [val.latest('date').data]
					waste_date = val.latest('date').date

	# Air
	air_values = []
	air_date = "-"


	if len(air_subs) != 0:
		for sub in air_subs:
			if str(sub.subtype.name) == Sensorsubtype.CO2:
				val = Value.objects.filter(subscription=sub.subscription_id)
				if val.exists():
					air_values += [val.latest('date').data]
					air_date = val.latest('date').date

	# Radiation
	radiation_values = []
	radiation_date = "-"


	if len(radiation_subs) != 0:
		for sub in radiation_subs:
			if str(sub.subtype.name) == Sensorsubtype.UV_RADIATION:
				val = Value.objects.filter(subscription=sub.subscription_id)
				if val.exists():
					radiation_values += [val.latest('date').data]
					radiation_date = val.latest('date').date

	# Sound
	sound_values = []
	sound_date = "-"


	if len(sound_subs) != 0:
		for sub in sound_subs:
			if str(sub.subtype.name) == Sensorsubtype.NOISE_LEVEL:
				val = Value.objects.filter(subscription=sub.subscription_id)
				if val.exists():
					sound_values += [val.latest('date').data]
					sound_date = val.latest('date').date


	# People
	people_values = []
	people_date = "-"


	if len(people_subs) != 0:
		for sub in people_subs:
			if str(sub.subtype.name) == Sensorsubtype.PEOPLE_COUNTER:
				val = Value.objects.filter(subscription=sub.subscription_id)
				if val.exists():
					if not sub.sensor.localization.address:
						people_values += [(val.latest('date').data, str(sub.sensor.localization))]
					else:
						people_values += [(val.latest('date').data, sub.sensor.localization.address)]
					people_date = val.latest('date').date


	# Illumination
	illumination_values = []
	illumination_date = "-"


	if len(illumination_subs) != 0:
		for sub in illumination_subs:
			if str(sub.subtype.name) == Sensorsubtype.LIGHTING_ACTUATOR:
				val = Value.objects.filter(subscription=sub.subscription_id)
				if val.exists():
					illumination_values += [val.latest('date').data]
					illumination_date = val.latest('date').date

	# Do temperature calculations
	if len(temp_values) == 0:
		avg = "-"
		maxim = "-"
		minim = "-"
	else:
		avg = round(sum(temp_values) / float(len(temp_values)),2)
		maxim = round(max(temp_values),2)
		minim = round(min(temp_values),2)

	# Do air calculations
	if len(air_values) == 0:
		air_avg = "-"
		air_max = "-"
		air_min = "-"

	else:
		air_avg = round(sum(air_values) / float(len(air_values)),2)
		air_max = round(max(air_values),2)
		air_min = round(min(air_values),2)


	# Do waste calculations
	if len(waste_values) == 0:
		up75 = "-"
		up50 = "-"
	else:
		up75 = sum(i>75 for i in waste_values)
		up50 = sum(i>50 and i<=75 for i in waste_values)


	# Do radiation calculations
	if len(radiation_values) == 0:
		up7 = "-"
		up4 = "-"
	else:
		up7 = sum(i>7 for i in radiation_values)
		up4 = sum(i>4 and i<=7 for i in radiation_values)

	# Do sound calculations
	if len(sound_values) == 0:
		sound_max = "-"
		sound_avg = "-"
	else:
		sound_max = max(sound_values)
		sound_avg = sum(sound_values)/len(sound_values)


	# Do people calculations
	if len(people_values) == 0:
		people_up75 = "-"
		people_up50 = "-"
	else:
		people_up75 = sum(i[0]>75 for i in people_values)
		people_up50 = sum(i[0]>50 and i<=75 for i in people_values)

	# Do illumination calculations
	if len(illumination_values) == 0:
		illumination_up75 = "-"
		illumination_up50 = "-"
	else:
		illumination_up75 = sum(i>75 for i in illumination_values)
		illumination_up50 = sum(i>50 and i<=75 for i in illumination_values)

	return {"temperature": {"max":maxim, "min":minim, "avg":avg, "active":len(temp_subs), "all":temp_notworking+len(temp_subs), "date":temp_date}, 
		"Illumination":{"date":illumination_date, "active": len(illumination_subs), "all":illumination_notworking+len(illumination_subs), "up75": illumination_up75, "up50": illumination_up50}, 
		"Air":{"max": air_max, "min":air_min, "average": air_avg, "units": "ppm", "subtype": "CO2", "active":len(air_subs), "all":air_notworking+len(air_subs), "date": air_date}, 
		"waste": {"up75":up75, "up50":up50, "active":len(waste_subs), "all":waste_notworking+len(waste_subs), "date":waste_date}, 
		"Sound": {"date":sound_date, "active":len(sound_subs), "all":sound_notworking+len(sound_subs),"max": sound_max, "average":sound_avg}, 
		"Radiation": {"date":radiation_date, "up7":up7, "up4":up4, "active":len(radiation_subs), "all":radiation_notworking+len(radiation_subs)}, 
		"People":{"date": people_date, "75":people_up75, "50":people_up50, "active":len(people_subs), "all": people_notworking+len(people_subs)}}


def get_subs_and_sensors(subs, s_type):

	temp_subs = []
	not_working_subs = []
	not_active_subs = []

	sensors = {}

	for s in subs:

		sensor = Sensor.objects.get(name=s.sensor)
		
		if sensor.sensor_type==s_type:

			if sensor not in sensors:
				# Sensor, last reading, active streams, inactive streams
				sensors[sensor] = [0,0,0]
			if sensor.active:
				if s.working:
					if str(s.subtype.name)!=Sensorsubtype.LATITUDE and str(s.subtype.name)!=Sensorsubtype.LONGITUDE:
						temp_subs += [s]
					sensors[sensor][1] += 1
				else:
					if str(s.subtype.name)!=Sensorsubtype.LATITUDE and str(s.subtype.name)!=Sensorsubtype.LONGITUDE:
						not_working_subs += [s]
					sensors[sensor][2] += 1
			else:
				if str(s.subtype.name)!=Sensorsubtype.LATITUDE and str(s.subtype.name)!=Sensorsubtype.LONGITUDE:
					not_active_subs += [s]

	return temp_subs, not_working_subs, not_active_subs, sensors

# If no date is specified, return all values
# Else, return only the values from the date until now
def get_values_by_subscriptions(days, weeks, hours, subs):
		
	values_subs = {}

	if days == None:
		days = 0
	else:
		days = int(days)

	if weeks == None:
		weeks = 0
	else:
		weeks = int(weeks)

	if hours == None:
		hours = 0
	else:
		hours = int(hours)

	for sub in subs:
		if days==0 and weeks==0 and hours==0:
			values_subs[sub.name] = Value.objects.filter(subscription_id=sub.subscription_id).values_list("date", "data")
		else:	
			values_subs[sub.name] = Value.objects.filter(subscription_id=sub.subscription_id, date__gte=timezone.now()-timezone.timedelta(days=days, weeks=weeks, hours=hours)).values_list("date", "data")
	return values_subs


def get_sensors_information(sensors):
	sen_list = []
	for sensor in sensors:
		sen_list += [{"id":sensor.device_id, "name":sensor.name, "information":sensor.information, "lat": Localization.objects.get(pk=sensor.localization.id).lat, "lon": Localization.objects.get(pk=sensor.localization.id).lon, "turned_on":sensor.active, "date":sensor.date_added, "active":sensors[sensor][1],"inactive":sensors[sensor][2], "all":sensors[sensor][1]+sensors[sensor][2], "streams":[sub.name for sub in Subscription.objects.filter(sensor=sensor) if sub.subtype.name!=Sensorsubtype.LATITUDE and sub.subtype.name!=Sensorsubtype.LONGITUDE], "address":sensor.localization.address}]

	return sen_list

def mobile_index(request, lat, lon):
	subtypes       = [Sensorsubtype.TEMPERATURE, Sensorsubtype.WASTE_FULLNESS, Sensorsubtype.UV_RADIATION, Sensorsubtype.NOISE_LEVEL, Sensorsubtype.PEOPLE_COUNTER, Sensorsubtype.CO2, Sensorsubtype.LIGHTING_ACTUATOR]
	allowed_subs   = []
	temp_sensubs   = []
	waste_sensubs  = []
	uv_sensubs     = []
	sound_sensubs  = []
	people_sensubs = []
	co2_sensubs    = []
	light_sensubs  = []

    	response = {}
    
	# Get allowed mobile subs of required subtypes
	tmp = get_mobile_subscriptions()

	for sub in tmp:
		if str(sub.subtype.name) in subtypes:
			allowed_subs += [sub]
	
	# Get allowed subs' sensors
	for sub in allowed_subs:
		if sub.working:
			sensor = Sensor.objects.get(name=sub.sensor)
			if sensor.active:
				if   str(sub.subtype.name) == Sensorsubtype.TEMPERATURE:
					temp_sensubs   += [(sensor, sub)]
				elif str(sub.subtype.name) == Sensorsubtype.WASTE_FULLNESS:
					waste_sensubs  += [(sensor, sub)]
				elif str(sub.subtype.name) == Sensorsubtype.UV_RADIATION:
					uv_sensubs     += [(sensor, sub)]
				elif str(sub.subtype.name) == Sensorsubtype.NOISE_LEVEL:
					sound_sensubs  += [(sensor, sub)]
				elif str(sub.subtype.name) == Sensorsubtype.PEOPLE_COUNTER:
					people_sensubs += [(sensor, sub)]
				elif str(sub.subtype.name) == Sensorsubtype.CO2:
					co2_sensubs    += [(sensor, sub)]
				elif str(sub.subtype.name) == Sensorsubtype.LIGHTING_ACTUATOR:
					light_sensubs  += [(sensor, sub)]
	
	# Calculate closest sensor for each subtype
	# And get its most recent value
	
	# Temperature
	temp_response = {'status': "Error", 'info': "No sensors nearby", 'value': None}
	temp_closest  = None
	temp_dist     = sys.float_info.max
	if len(temp_sensubs) > 0:
		temp_response['info'] = "A sensor was found"
		# Get closest sensor
		for sensub in temp_sensubs:
			dist = haversine(float(lat),float(lon), sensub[0].localization.lat,sensub[0].localization.lon)
			if dist <= temp_dist:
				temp_dist    = dist 
				temp_closest = sensub
		
		# Get most recent value
		val = Value.objects.filter(subscription=temp_closest[1].subscription_id)
		if val.exists():
			temp_response['value']  = val.latest('date').data
            		temp_response['status'] = "OK"
        	else:
            		temp_response['info']   = "Sensor has no values"
	response['temperature'] = temp_response
    
	# Waste
	waste_response = {'status': "Error", 'info': "No sensors nearby", 'value': None}
	waste_closest  = None
	waste_dist     = sys.float_info.max
	if len(waste_sensubs) > 0:
        	waste_response['info'] = "A sensor was found"
		# Get closest sensor
		for sensub in waste_sensubs:
			dist = haversine(float(lat),float(lon), sensub[0].localization.lat,sensub[0].localization.lon)
			if dist <= waste_dist:
				waste_dist    = dist 
				waste_closest = sensub
		
		# Get most recent value
		val = Value.objects.filter(subscription=waste_closest[1].subscription_id)
		if val.exists():
			waste_response['value']  = val.latest('date').data
            		waste_response['status'] = "OK"
        	else:
            		waste_response['info']   = "Sensor has no values"
	response['waste'] = waste_response
	
	# UV
	uv_response = {'status': "Error", 'info': "No sensors nearby", 'value': None}
	uv_closest  = None
	uv_dist     = sys.float_info.max
	if len(uv_sensubs) > 0:
        	uv_response['info'] = "A sensor was found"
		# Get closest sensor
		for sensub in uv_sensubs:
			dist = haversine(float(lat),float(lon), sensub[0].localization.lat,sensub[0].localization.lon)
			if dist <= uv_dist:
				uv_dist    = dist 
				uv_closest = sensub
		
		# Get most recent value
		val = Value.objects.filter(subscription=uv_closest[1].subscription_id)
		if val.exists():
			uv_response['value']  = val.latest('date').data
            		uv_response['status'] = "OK"
        	else:
            		uv_response['info']   = "Sensor has no values"
	response['uv'] = uv_response

	# Sound
	sound_response = {'status': "Error", 'info': "No sensors nearby", 'value': None}
	sound_closest  = None
	sound_dist     = sys.float_info.max
	if len(sound_sensubs) > 0:
        	sound_response['info'] = "A sensor was found"
		# Get closest sensor
		for sensub in sound_sensubs:
			dist = haversine(float(lat),float(lon), sensub[0].localization.lat,sensub[0].localization.lon)
			if dist <= sound_dist:
				sound_dist    = dist 
				sound_closest = sensub
		
		# Get most recent value
		val = Value.objects.filter(subscription=sound_closest[1].subscription_id)
		if val.exists():
			sound_response['value']  = val.latest('date').data
            		sound_response['status'] = "OK"
        	else:
            		sound_response['info']   = "Sensor has no values"
	response['sound'] = sound_response

	# People
	people_response = {'status': "Error", 'info': "No sensors nearby", 'value': None}
	people_closest = None
	people_dist    = sys.float_info.max
	if len(people_sensubs) > 0:
		people_response['info'] = "A sensor was found"
		# Get closest sensor
		for sensub in people_sensubs:
			dist = haversine(float(lat),float(lon), sensub[0].localization.lat,sensub[0].localization.lon)
			if dist <= people_dist:
				people_dist    = dist 
				people_closest = sensub
		
		# Get most recent value
		val = Value.objects.filter(subscription=people_closest[1].subscription_id)
		if val.exists():
			people_response['value']  = val.latest('date').data
            		people_response['status'] = "OK"
        	else:
            		people_response['info']   = "Sensor has no values"
	response['people'] = people_response

	# CO2
	co2_response = {'status': "Error", 'info': "No sensors nearby", 'value': None}
	co2_closest = None
	co2_dist    = sys.float_info.max
	if len(co2_sensubs) > 0:
		co2_response['info'] = "A sensor was found"
		# Get closest sensor
		for sensub in co2_sensubs:
			dist = haversine(float(lat),float(lon), sensub[0].localization.lat,sensub[0].localization.lon)
			if dist <= co2_dist:
				co2_dist    = dist 
				co2_closest = sensub
		
		# Get most recent value
		val = Value.objects.filter(subscription=co2_closest[1].subscription_id)
		if val.exists():
			co2_response['value']  = val.latest('date').data
            		co2_response['status'] = "OK"
        	else:
            		co2_response['info']   = "Sensor has no values"
	response['co2'] = co2_response
    
	# Light
	light_response = {'status': "Error", 'info': "No sensors nearby", 'value': None}
	light_closest = None	
	light_dist    = sys.float_info.max
	if len(light_sensubs) > 0:
		light_response['info'] = "A sensor was found"
		# Get closest sensor
		for sensub in light_sensubs:
			dist = haversine(float(lat),float(lon), sensub[0].localization.lat,sensub[0].localization.lon)
			if dist <= light_dist:
				light_dist    = dist 
				light_closest = sensub
		
		# Get most recent value
		val = Value.objects.filter(subscription=light_closest[1].subscription_id)
		if val.exists():
			light_response['value']  = val.latest('date').data
            		light_response['status'] = "OK"
        	else:
            		light_response['info']   = "Sensor has no values"
	response['light'] = light_response
	
	return JsonResponse(response)

def haversine(lat1, lon1, lat2, lon2):
	# convert decimal degrees to radians 
	lat1 = radians(lat1)
	lon1 = radians(lon1)
	lat2 = radians(lat2)
	lon2 = radians(lon2)

	# haversine formula 
	dlat = lat2 - lat1 
	dlon = lon2 - lon1 
	d = sin(dlat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(dlon * 0.5) ** 2
	h = 2 * 6371 * asin(sqrt(d)) 
	return h

def mobile_map(request):
	subtypes = [Sensorsubtype.TEMPERATURE, Sensorsubtype.WASTE_FULLNESS, Sensorsubtype.UV_RADIATION, Sensorsubtype.NOISE_LEVEL, Sensorsubtype.PEOPLE_COUNTER, Sensorsubtype.CO2, Sensorsubtype.LIGHTING_ACTUATOR, Sensorsubtype.AIR_PRESSURE]
	sensub   = []
	sen_list = []
	
	# Get the allowed subscriptions
	# And the sensor related
	tmp = get_mobile_subscriptions()
	for sub in tmp:
		if str(sub.subtype.name) in subtypes:
			sensub += [(Sensor.objects.get(name=sub.sensor), sub)]

	# Get lastest value from each sub
	for sensor, sub in sensub:
		val = Value.objects.filter(subscription=sub.subscription_id)
		if val.exists():
	    		latest = round(val.latest('date').data, 2)
		else:
	    		latest = None

		sen_list += [{"id":sensor.device_id, "name":sensor.name, "type":sensor.sensor_type, "lat": Localization.objects.get(pk=sensor.localization.id).lat, "lon": Localization.objects.get(pk=sensor.localization.id).lon, "sub_name":sub.name, "sub_id":sub.subscription_id, "sub_value": latest}]
 
	return JsonResponse({"sensors":sen_list})  

def mobile_temperature(request, weeks=None, days=None, hours=None):
	sensors, values = get_temp_data('public_mobile', weeks, days, hours)
	
	return JsonResponse( {"sensors":sensors, "values":values})

def mobile_lighting(request, weeks=None, days=None, hours=None):
	sensors, ill_values, act_values = get_lighting_data('public_mobile', weeks, days, hours)
	return JsonResponse( {"sensors":sensors, "values":act_values})
	
def mobile_air(request, weeks=None, days=None, hours=None):
	sensors, pressure_values, co2_values = get_air_data('public_mobile', weeks, days, hours)
	
	return JsonResponse( {"sensors":sensors, "pressure":pressure_values, "co2":co2_values})

def mobile_waste(request, weeks=None, days=None, hours=None):
	sensors, values, values_temp_values, values_vol_values = get_waste_data('public_mobile', weeks, days, hours)
	
	return JsonResponse ({"sensors":sensors, "waste_fullness":values})
	
def mobile_noise(request, weeks=None, days=None, hours=None):
	sensors, values = get_noise_data('public_mobile', weeks, days, hours)
	
	return JsonResponse( {"sensors":sensors, "values":values})

def mobile_radiation(request, weeks=None, days=None, hours=None):
	sensors, values, vis_values, red_values = get_radiation_data('public_mobile', weeks, days, hours)	
	
	return JsonResponse( {"sensors":sensors, "uvindex":values})

def mobile_people(request, weeks=None, days=None, hours=None):
	sensors, values = get_people_data('public_mobile', weeks, days, hours)
	
	return JsonResponse( {"sensors":sensors, "values":values})

def get_temp_data(user, weeks=None, days=None, hours=None):
	temp_subs = []
	not_working_subs = []
	not_active_subs = []

	sensors = {}
	values_subs = {}

	# Get the allowed subscriptions
	# Filter subscriptions by type
	if user == 'public_mobile':
		subs = get_mobile_subscriptions()
	else:
		subs = get_subscriptions(user)
	temp_subs, not_working_subs, not_active_subs, sensors = get_subs_and_sensors(subs, Sensor.TEMPERATURE)

	values_subs = get_values_by_subscriptions(days, weeks, hours, temp_subs+not_working_subs+not_active_subs)

	# Get sensors' information
	sen_list = get_sensors_information(sensors)
	
	values = [{s:[[[v[0].year, v[0].month, v[0].day, v[0].hour, v[0].minute],v[1]] for v in values_subs[s]]} for s in values_subs]
	
	return sen_list, values

def get_lighting_data(user, weeks=None, days=None, hours=None):
	ill_subs = []
	act_subs = []

	ill_not_working_subs = []
	act_not_working_subs = []

	ill_not_active_subs = []
	act_not_active_subs = []

	sensors = {}
	ill_values_subs = {}
	act_values_subs = {}

	# Get the allowed subscriptions
	# Filter subscriptions by type
	if user == 'public_mobile':
		subs = get_mobile_subscriptions()
	else:
		subs = get_subscriptions(user)

	for s in subs:

		sensor = Sensor.objects.get(name=s.sensor)

		if sensor.sensor_type==Sensor.LIGHTING:

			if sensor not in sensors:
				# Sensor, last reading, active streams, inactive streams
				sensors[sensor] = [0,0,0]
			if sensor.active:
				if s.working:
					if str(s.subtype.name)==Sensorsubtype.LIGHTING_ILLUMINATION:
						ill_subs += [s]
					elif str(s.subtype.name)==Sensorsubtype.LIGHTING_ACTUATOR:
						act_subs += [s]
					sensors[sensor][1] += 1
				else:
					if str(s.subtype.name)==Sensorsubtype.LIGHTING_ILLUMINATION:
						ill_not_working_subs += [s]
					elif str(s.subtype.name)==Sensorsubtype.LIGHTING_ACTUATOR:
						act_not_working_subs += [s]
					sensors[sensor][2] += 1
			else:
				if str(s.subtype.name)==Sensorsubtype.LIGHTING_ILLUMINATION:
					ill_not_active_subs += [s]
				elif str(s.subtype.name)==Sensorsubtype.LIGHTING_ACTUATOR:
					act_not_active_subs += [s]


	# If no date is specified, return all values
	# Else, return only the values from the date until now

	ill_values_subs = get_values_by_subscriptions(days, weeks, hours, ill_subs+ill_not_working_subs+ill_not_active_subs)

	act_values_subs = get_values_by_subscriptions(days, weeks, hours, act_subs+act_not_working_subs+act_not_active_subs)

	# Get sensors' information
	sen_list = get_sensors_information(sensors)

	ill_values = [{s:[[[v[0].year, v[0].month, v[0].day, v[0].hour, v[0].minute],v[1]] for v in ill_values_subs[s]]} for s in ill_values_subs]
	act_values = [{s:[[[v[0].year, v[0].month, v[0].day, v[0].hour, v[0].minute],v[1]] for v in act_values_subs[s]]} for s in act_values_subs]

	return sen_list, ill_values, act_values

def get_air_data(user, weeks=None, days=None, hours=None):
	pressure_subs = []
	co2_subs = []

	pressure_not_working_subs = []
	co2_not_working_subs = []

	pressure_not_active_subs = []
	co2_not_active_subs = []

	sensors = {}
	pressure_values_subs = {}
	co2_values_subs = {}

	# Get the allowed subscriptions
	# Filter subscriptions by type
	if user == 'public_mobile':
		subs = get_mobile_subscriptions()
	else:
		subs = get_subscriptions(user)

	for s in subs:

		sensor = Sensor.objects.get(name=s.sensor)

		if sensor.sensor_type==Sensor.AIR:

			if sensor not in sensors:
				# Sensor, last reading, active streams, inactive streams
				sensors[sensor] = [0,0,0]
			if sensor.active:
				if s.working:
					if str(s.subtype.name)==Sensorsubtype.AIR_PRESSURE:
						pressure_subs += [s]
					elif str(s.subtype.name)==Sensorsubtype.CO2:
						co2_subs += [s]
					sensors[sensor][1] += 1
				else:
					if str(s.subtype.name)==Sensorsubtype.AIR_PRESSURE:
						pressure_not_working_subs += [s]
					elif str(s.subtype.name)==Sensorsubtype.CO2:
						co2_not_working_subs += [s]
					sensors[sensor][2] += 1
			else:
				if str(s.subtype.name)==Sensorsubtype.AIR_PRESSURE:
					pressure_not_active_subs += [s]
				elif str(s.subtype.name)==Sensorsubtype.CO2:
					co2_not_active_subs += [s]


	# If no date is specified, return all values
	# Else, return only the values from the date until now

	pressure_values_subs = get_values_by_subscriptions(days, weeks, hours, pressure_subs+pressure_not_working_subs+pressure_not_active_subs)

	co2_values_subs = get_values_by_subscriptions(days, weeks, hours, co2_subs+co2_not_working_subs+co2_not_active_subs)

	# Get sensors' information
	sen_list = get_sensors_information(sensors)

	pressure_values = [{s:[[[v[0].year, v[0].month, v[0].day, v[0].hour, v[0].minute],v[1]] for v in pressure_values_subs[s]]} for s in pressure_values_subs]
	co2_values = [{s:[[[v[0].year, v[0].month, v[0].day, v[0].hour, v[0].minute],v[1]] for v in co2_values_subs[s]]} for s in co2_values_subs]

	return sen_list, pressure_values, co2_values

def get_waste_data(user, weeks=None, days=None, hours=None):
	waste_subs = []
	temp_subs = []
	vol_subs = []
	not_working_subs = []
	not_working_temp_subs = []
	not_working_vol_subs = []
	not_active_subs = []
	not_active_temp_subs = []
	not_active_vol_subs = []

	sensors = {}
	values_subs = {}
	values_temp_subs = {}

	# Get the allowed subscriptions
	# Filter subscriptions by type
	if user == 'public_mobile':
		subs = get_mobile_subscriptions()
	else:
		subs = get_subscriptions(user)

	for s in subs:

		sensor = Sensor.objects.get(name=s.sensor)

		if sensor.sensor_type==Sensor.WASTE:

			if sensor not in sensors:
				# Sensor, last reading, active streams, inactive streams
				sensors[sensor] = [0,0,0]
			if sensor.active:
				if s.working:
					if str(s.subtype.name)==Sensorsubtype.WASTE_FULLNESS:
						waste_subs += [s]
					elif str(s.subtype.name)==Sensorsubtype.WASTE_INTERNAL_TEMPERATURE:
						temp_subs += [s]
					elif str(s.subtype.name)==Sensorsubtype.WASTE_VOLUME:
						vol_subs += [s]
					sensors[sensor][1] += 1
				else:
					if str(s.subtype.name)==Sensorsubtype.WASTE_FULLNESS:
						not_working_subs += [s]
					elif str(s.subtype.name)==Sensorsubtype.WASTE_INTERNAL_TEMPERATURE:
						not_working_temp_subs += [s]
					elif str(s.subtype.name)==Sensorsubtype.WASTE_VOLUME:
						not_working_vol_subs += [s]
					sensors[sensor][2] += 1
			else:
				if str(s.subtype.name)==Sensorsubtype.WASTE_FULLNESS:
					not_active_subs += [s]
				elif str(s.subtype.name)==Sensorsubtype.WASTE_INTERNAL_TEMPERATURE:
					not_active_temp_subs += [s]
				elif str(s.subtype.name)==Sensorsubtype.WASTE_VOLUME:
					not_active_vol_subs += [s]


	# If no date is specified, return all values
	# Else, return only the values from the date until now

	values_subs = get_values_by_subscriptions(days, weeks, hours, waste_subs+not_working_subs+not_active_subs)

	values_temp_subs = get_values_by_subscriptions(days, weeks, hours, temp_subs+not_working_temp_subs+not_active_temp_subs)

	values_vol_subs = get_values_by_subscriptions(days, weeks, hours, vol_subs+not_working_vol_subs+not_active_vol_subs)


	# Get sensors' information
	sen_list = get_sensors_information(sensors)

	values = [{s:[[[v[0].year, v[0].month, v[0].day, v[0].hour, v[0].minute],v[1]] for v in values_subs[s]]} for s in values_subs]
	values_temp_values = [{s:[[[v[0].year, v[0].month, v[0].day, v[0].hour, v[0].minute],v[1]] for v in values_temp_subs[s]]} for s in values_temp_subs]
	values_vol_values = [{s:[[[v[0].year, v[0].month, v[0].day, v[0].hour, v[0].minute],v[1]] for v in values_vol_subs[s]]} for s in values_vol_subs]
	

	return sen_list, values, values_temp_values, values_vol_values

def get_noise_data(user, weeks=None, days=None, hours=None):
	sound_subs = []
	not_working_subs = []
	not_active_subs = []

	sensors = {}
	values_subs = {}

	# Get the allowed subscriptions
	# Filter subscriptions by type
	if user == 'public_mobile':
		subs = get_mobile_subscriptions()
	else:
		subs = get_subscriptions(user)

	sound_subs, not_working_subs, not_active_subs, sensors = get_subs_and_sensors(subs, Sensor.NOISE)

	values_subs = get_values_by_subscriptions(days, weeks, hours, sound_subs+not_working_subs+not_active_subs)

	# Get sensors' information
	sen_list = get_sensors_information(sensors)

	values = [{s:[[[v[0].year, v[0].month, v[0].day, v[0].hour, v[0].minute],v[1]] for v in values_subs[s]]} for s in values_subs]

	return sen_list, values

def get_radiation_data(user, weeks=None, days=None, hours=None):
	uv_subs = []
	uv_not_working_subs = []
	uv_not_active_subs = []

	vis_subs = []
	vis_not_working_subs = []
	vis_not_active_subs = []

	red_subs = []
	red_not_working_subs = []
	red_not_active_subs = []

	sensors = {}
	values_subs = {}

	# Get the allowed subscriptions
	# Filter subscriptions by type
	if user == 'public_mobile':
		subs = get_mobile_subscriptions()
	else:
		subs = get_subscriptions(user)

	for s in subs:
		sensor = Sensor.objects.get(name=s.sensor)

		if sensor.sensor_type==Sensor.RADIATION:

			if sensor not in sensors:
				# Sensor, last reading, active streams, inactive streams
				sensors[sensor] = [0,0,0]
			if sensor.active:
				if s.working:
					if str(s.subtype.name)==Sensorsubtype.UV_RADIATION:
						uv_subs += [s]
					elif str(s.subtype.name)==Sensorsubtype.VISIBLE_RADIATION:
						vis_subs += [s]
					elif str(s.subtype.name)==Sensorsubtype.INFRARED_RADIATION:
						red_subs += [s]
					sensors[sensor][1] += 1
				else:
					if str(s.subtype.name)==Sensorsubtype.UV_RADIATION:
						uv_not_working_subs += [s]
					elif str(s.subtype.name)==Sensorsubtype.VISIBLE_RADIATION:
						vis_not_working_subs += [s]
					elif str(s.subtype.name)==Sensorsubtype.INFRARED_RADIATION:
						red_not_working_subs += [s]
					sensors[sensor][2] += 1
			else:
				if str(s.subtype.name)==Sensorsubtype.UV_RADIATION:
					uv_active_subs += [s]
				elif str(s.subtype.name)==Sensorsubtype.VISIBLE_RADIATION:
					vis_active_temp_subs += [s]
				elif str(s.subtype.name)==Sensorsubtype.INFRARED_RADIATION:
					red_not_active_subs += [s]

	values_subs = get_values_by_subscriptions(days, weeks, hours, uv_subs+uv_not_working_subs+uv_not_active_subs)

	vis_values_subs = get_values_by_subscriptions(days, weeks, hours, vis_subs+vis_not_working_subs+vis_not_active_subs)

	red_values_subs = get_values_by_subscriptions(days, weeks, hours, red_subs+red_not_working_subs+red_not_active_subs)

	# Get sensors' information
	sen_list = get_sensors_information(sensors)

	values = [{s:[[[v[0].year, v[0].month, v[0].day, v[0].hour, v[0].minute],v[1]] for v in values_subs[s]]} for s in values_subs]
	vis_values = [{s:[[[v[0].year, v[0].month, v[0].day, v[0].hour, v[0].minute],v[1]] for v in vis_values_subs[s]]} for s in vis_values_subs]
	red_values = [{s:[[[v[0].year, v[0].month, v[0].day, v[0].hour, v[0].minute],v[1]] for v in red_values_subs[s]]} for s in red_values_subs]

	return sen_list, values, vis_values, red_values

def get_people_data(user, weeks=None, days=None, hours=None):
	people_subs = []
	not_working_subs = []
	not_active_subs = []

	sensors = {}
	values_subs = {}

	# Get the allowed subscriptions
	# Filter subscriptions by type
	if user == 'public_mobile':
		subs = get_mobile_subscriptions()
	else:
		subs = get_subscriptions(user)

	people_subs, not_working_subs, not_active_subs, sensors = get_subs_and_sensors(subs, Sensor.PEOPLE)

	values_subs = get_values_by_subscriptions(days, weeks, hours, people_subs+not_working_subs+not_active_subs)

	# Get sensors' information
	sen_list = get_sensors_information(sensors)

	values = [{s:[[[v[0].year, v[0].month, v[0].day, v[0].hour, v[0].minute],v[1]] for v in values_subs[s]]} for s in values_subs]

	return sen_list, values

# Get all types of sensors of a user
def get_types(request):

	types = []
	subs = get_subscriptions(request.user)
	for s in subs:
		sensor = Sensor.objects.get(name=s.sensor)
		# Get the types from the streams allowed
		if sensor.sensor_type==Sensor.WASTE:
			if Sensor.WASTE not in types:
				types += [Sensor.WASTE]
		elif sensor.sensor_type==Sensor.LIGHTING:
			if Sensor.LIGHTING not in types:
				types += [Sensor.LIGHTING]
		elif sensor.sensor_type==Sensor.PEOPLE:
			if Sensor.PEOPLE not in types:
				types += [Sensor.PEOPLE]
		elif sensor.sensor_type==Sensor.NOISE:
			if Sensor.NOISE not in types:
				types += [Sensor.NOISE]
		elif sensor.sensor_type==Sensor.TEMPERATURE:
			if Sensor.TEMPERATURE not in types:
				types += [Sensor.TEMPERATURE]
		elif sensor.sensor_type==Sensor.RADIATION:
			if Sensor.RADIATION not in types:
				types += [Sensor.RADIATION]
		elif sensor.sensor_type==Sensor.AIR:
			if Sensor.AIR not in types:
				types += [Sensor.AIR]

	return types

# API to send a user report from mobile
@csrf_exempt
def mobile_report(request):
	if request.method == 'GET':
		raise Http404
	if request.method == 'POST':
		try:
			user_name = ""
			filename = ""
			date = datetime.datetime.now()
			title = request.POST.get("title")
			information = request.POST.get("information")
			email = request.POST.get("email")
			user_name = request.POST.get("username")
			subscription_id = request.POST.get("subscription")
			subscription = Subscription.objects.get(subscription_id=subscription_id)
		except Exception as e:
			print e
			return JsonResponse({'status': 'Error', 'info': 'Wrong parameters send in request body.'})
		
		try:
			r = UserReport(date=date, title=title, information=information, subscription=subscription, state=UserReport.NOT_SEEN, working_state=UserReport.WAITING)
			
			if email:
				r.email = email

			if user_name:
				r.user_name = user_name
			
			r.save()

			for file in request.FILES.getlist('files'):
				ra = ReportAttach(document = file)
				ra.save()
				r.attach.add(ra)

		except Exception as e:
			print e
			return JsonResponse({'status': 'Error', 'info': 'Could not add report'})

		return JsonResponse({'status': 'OK', 'info': 'Report successfully added.'})

## Function to get all subscriptions of user
def get_subscriptions(user):
	subs = Subscription_Group.objects.filter(users=user)
	all_subs = list(set([s for sub in subs for s in sub.subscriptions.all() if s != None]))
	return all_subs


def get_mobile_subscriptions():
	sub = Subscription_Group.objects.get(name="public_mobile")
	all_subs = list(set([s for s in sub.subscriptions.all() if s != None]))
	return all_subs

