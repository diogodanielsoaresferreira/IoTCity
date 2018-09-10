from __future__ import unicode_literals
from django.db import models
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import User
import magic
import os


class Localization(models.Model):
	lat = models.FloatField()
	lon = models.FloatField()
	address = models.TextField(null=True, blank=True)
	
	def __unicode__(self):
		return str(self.lat)+";"+str(self.lon)

	class Meta:
		verbose_name = "Localization"
		verbose_name_plural = "Localizations"

class day_week(models.Model):
	MONDAY = 'MO'
	TUESDAY = 'TU'
	WEDNESDAY = 'WE'
	THURSDAY = 'TH'
	FRIDAY = 'FR'
	SATURDAY = 'SA'
	SUNDAY = 'SU'
	DAYS_OF_WEEK = (
		(MONDAY, 'Monday'),
		(TUESDAY, 'Tuesday'),
		(WEDNESDAY, 'Wednesday'),
		(THURSDAY, 'Thursday'),
		(FRIDAY, 'Friday'),
		(SATURDAY, 'Saturday'),
		(SUNDAY, 'Sunday'),
	)
	day = models.CharField(max_length=2, choices=DAYS_OF_WEEK)

	def __unicode__(self):
		return dict(self.DAYS_OF_WEEK)[self.day]

	class Meta:
		verbose_name_plural = "days_week"

class day_year(models.Model):
	day = models.DateField()

	def __unicode__(self):
		return str(self.day)

	class Meta:
		verbose_name = "Day"
		verbose_name_plural = "Days"

class Sensor(models.Model):

	device_id = models.TextField(max_length=50, primary_key=True)
	name = models.TextField(max_length=50, unique=True)
	date_added = models.DateTimeField()
	information = models.TextField(null=True, blank=True)

	TEMPERATURE = 'TE'
	AIR = 'AI'
	WASTE = 'WA'
	NOISE = 'SO'
	PEOPLE = 'PE'
	LIGHTING = 'IL'
	RADIATION = 'RA'

	TYPE_CHOICES = (
		(TEMPERATURE, 'Temperature'),
		(AIR, 'Air'),
		(WASTE, 'Waste'),
		(NOISE, 'Noise'),
		(PEOPLE, 'People'),
		(LIGHTING, 'Lighting'),
		(RADIATION, 'Radiation'),
	)


	NOT_SEEN = 'NS'
	SEEN = 'SE'
	STATE_CHOICES = (
		(NOT_SEEN, 'Not Seen'),
		(SEEN, 'Seen'),
	)

	state = models.CharField(max_length=2, choices=STATE_CHOICES, null=False, blank=False, default=SEEN)
	
	sensor_type = models.CharField(max_length=2, choices=TYPE_CHOICES)
	
	# Determines if the sensor is currently active or not
	active = models.BooleanField(default=True)

	localization = models.ForeignKey('Localization', on_delete=models.CASCADE)

	def __unicode__(self):
		return str(self.name)

	class Meta:
		ordering = ('date_added',)
		verbose_name = "Sensor"
		verbose_name_plural = "Sensors"

class Sensorsubtype(models.Model):

	LIGHTING_ACTUATOR = 'LA'
	CO2 = 'C2'
	VISIBLE_RADIATION = 'VR'
	INFRARED_RADIATION = 'IR'
	WASTE_VOLUME = 'WV'
	WASTE_INTERNAL_TEMPERATURE = 'WT'
	LIGHTING_ILLUMINATION = 'LI'
	PEOPLE_COUNTER = 'PC'
	NOISE_LEVEL = 'NL'
	UV_RADIATION = 'UV'
	AIR_PRESSURE = 'AP'
	WASTE_FULLNESS = 'WP'
	TEMPERATURE = 'TE'
	LATITUDE = 'LT'
	LONGITUDE = 'LO'

	SUBTYPE_CHOICES = (
		(LIGHTING_ACTUATOR,'Dimming'),
		(CO2,'CO2'),
		(VISIBLE_RADIATION,'Visible Radiation'),
		(INFRARED_RADIATION,'Infrared Radiation'),
		(WASTE_VOLUME,'Waste Volume'),
		(WASTE_INTERNAL_TEMPERATURE,'Waste Internal Temperature'),
		(LIGHTING_ILLUMINATION,'Lighting Illumination'),
		(PEOPLE_COUNTER,'People Counter'),
		(NOISE_LEVEL,'Noise Level'),
		(UV_RADIATION,'UV Radiation'),
		(AIR_PRESSURE,'Air Pressure'),
		(WASTE_FULLNESS,'Waste Fullness Percentage'),
		(TEMPERATURE,'Temperature'),
		(LATITUDE, 'Latitude'),
		(LONGITUDE, 'Longitude'),
	)

	name = models.CharField(max_length=2, choices=SUBTYPE_CHOICES, unique=True)

	def __unicode__(self):
		return str(dict(self.SUBTYPE_CHOICES)[self.name])


class Subscription(models.Model):

	subscription_id = models.CharField(primary_key=True, max_length=36)
	name = models.TextField(max_length=50, unique=True)
	date_added = models.DateTimeField()
	
	# Determines if the server is receiving data from that sensor
	working = models.BooleanField(default=True)

	subtype = models.ForeignKey('Sensorsubtype', on_delete=models.CASCADE, null=True, blank=True)


	# Determines if the subscription is a sender or a receiver
	# If is a sender, sends data to server. Otherwise, receives data from the server
	sender = models.BooleanField(default=True)

	sensor = models.ForeignKey('Sensor', on_delete=models.CASCADE)

	def __unicode__(self):
		return str(self.name)

	class Meta:
		ordering = ('date_added',)
		verbose_name = "Subscription"
		verbose_name_plural = "Subscriptions"


class UserReport(models.Model):
	
	date = models.DateTimeField()
	title = models.CharField(max_length=50, default="")
	information = models.TextField()
	email = models.EmailField(null=True, blank=True)
	user_name = models.TextField(null=True, blank=True)
	subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE, null=True, blank=True)


	NOT_SEEN = 'NS'
	SEEN = 'SE'
	TYPE_CHOICES = (
		(NOT_SEEN, 'Not Seen'),
		(SEEN, 'Seen'),
	)

	state = models.CharField(max_length=2, choices=TYPE_CHOICES)

	WAITING = 'WA'
	WORKING_ON_IT = 'WI'
	SOLVED = 'SO'
	WORKING_CHOICES = (
		(WAITING, 'Waiting'),
		(WORKING_ON_IT, 'Working On'),
		(SOLVED, 'Solved'),
	)

	deleted = models.BooleanField(default=False)

	working_state = models.CharField(max_length=2, choices=WORKING_CHOICES, default=WAITING)

	attach = models.ManyToManyField('ReportAttach', blank=True)

	def __unicode__(self):
		return self.information

	class Meta:
		ordering = ('date',)
		verbose_name = "Citizen Report"
		verbose_name_plural = "Citizen Reports"


class Value(models.Model):
	
	data = models.FloatField()
	timeToLive = models.IntegerField(blank=True, null=True, default=120)
	date = models.DateTimeField()
	
	subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE)

	def __unicode__(self):
		return str(self.data)

	class Meta:
		ordering = ('date',)
		verbose_name = "Value from stream"
		verbose_name_plural = "Values from Streams"


class Note(models.Model):

	date_beginning = models.DateTimeField()
	date_end = models.DateTimeField()
	name = models.TextField(max_length=50, blank=False)

	ACTIVE = 'AC'
	INACTIVE = 'IN'

	STATE_CHOICES = (
		(ACTIVE, 'Active'),
		(INACTIVE, 'Inactive'),
		)

	state = models.CharField(max_length=2, choices=STATE_CHOICES, default=ACTIVE)

	information = models.TextField()

	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __unicode__(self):
		return str(self.name)

	class Meta:
		ordering = ('date_beginning',)
		verbose_name = "Note"
		verbose_name_plural = "Notes"

class Alarm(models.Model):
	
	subscriptions = models.ManyToManyField('Subscription')
	name = models.TextField(max_length=50)

	MAX = 'MAX'
	MIN = 'MIN'
	ALARM_CHOICES = (
		(MAX, 'Maximum'),
		(MIN, 'Minimum'),
	)
	type_alarm = models.CharField(max_length=3, choices=ALARM_CHOICES, default=MAX, blank=True, null=True)
	has_threshold = models.BooleanField(default=True)
	threshold = models.FloatField(null=True, blank=True)

	date_created = models.DateTimeField()


	daysOfWeek = models.ManyToManyField(day_week, blank=True)


	beg_date = models.DateTimeField(blank=True, null=True)
	end_date = models.DateTimeField(blank=True, null=True)


	hours_active_beg = models.TimeField(null=True, blank=True)
	hours_active_end = models.TimeField(null=True, blank=True)

	ACTIVE = 'AC'
	DELETED = 'DE'
	ALARM_STATE=(
		('AC', 'Active'),
		('DE', 'Deleted'),
		)
	state = models.CharField(max_length=2, choices=ALARM_STATE, default=ACTIVE)

	
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __unicode__(self):
		return str(self.date_created)

	class Meta:
		ordering = ('date_created',)
		verbose_name = "Alert"
		verbose_name_plural = "Alarms"


class AlarmActuator(models.Model):
	value = models.IntegerField()

	alarm = models.ForeignKey('Alarm', on_delete=models.CASCADE, default=None)
	subscriptions = models.ManyToManyField(Subscription, blank=True)

	def __unicode__(self):
		return str(self.value)

	class Meta:
		verbose_name = "Actuator of Alert"
		verbose_name_plural = "Actuators of Alert"


class Subscription_Group(models.Model):
	name = models.TextField(max_length=50)
	information = models.TextField(null=True, blank=True)

	users = models.ManyToManyField(User, blank=True)
	subscriptions = models.ManyToManyField('subscription', blank=True)

	def __unicode__(self):
		return str(self.name)

	class Meta:
		verbose_name = "Subscription Group"
		verbose_name_plural = "Subscription Groups"


class Triggered_alarm(models.Model):
	
	ACTIVE = 'AC'
	NOT_SEEN = 'NS'
	SEEN = 'SE'

	STATE_CHOICES = (
		(ACTIVE, 'Active'),
		(NOT_SEEN, 'Not Seen'),
		(SEEN, 'Seen'),
	)

	deleted = models.BooleanField(default=False)

	state = models.CharField(max_length=2, choices=STATE_CHOICES)
	alarm = models.ForeignKey('Alarm', on_delete=models.CASCADE)
	value = models.ManyToManyField('Value')

	class Meta:
		verbose_name = "Triggered Alarm"
		verbose_name_plural = "Triggered Alarms"


class ReportAttach(models.Model):
	document = models.FileField(upload_to='uploads/')

	def filename(self):
		return os.path.basename(self.document.name)

	def extension(self):
		name, extension = os.path.splitext(self.document.name)
		mag = magic.from_file(self.document.name, mime=True)

		try:
			s = mag.split("/")[0]
			if s=='audio' or s=='video' or s=='image' or s=='text':
				return s
		except Exception as e:
			return mag

	def __unicode__(self):
		return str(self.document.name)

	class Meta:
		verbose_name = "Attachment"
		verbose_name_plural = "Report Attachments"