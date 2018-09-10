from django.contrib import admin
from django.contrib.auth.models import Group
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django_celery_results.models import TaskResult
import fcm_django.admin
from fcm_django.models import FCMDevice, Device, FCMDeviceManager, FCMDeviceQuerySet
from .models import *


class Sensor_Admin(admin.ModelAdmin):
	list_display = ('device_id', 'name', 'date_added', 'sensor_type', 'active', 'state',)
	search_fields = ('device_id', 'name', 'sensor_type','state',)

class Subscription_Admin(admin.ModelAdmin):
	list_display = ('subscription_id', 'name', 'sensor', 'working', 'subtype',  'sender')
	search_fields = ('subscription_id', 'name', 'sensor__name',)

class Value_Admin(admin.ModelAdmin):
	list_display = ('subscription', 'data', 'date', 'sensor',)
	search_fields = ('subscription__name',)

	def sensor(self, obj):
		return obj.subscription.sensor

class Subscription_Group_Admin(admin.ModelAdmin):
	filter_horizontal = ('users','subscriptions',)
	search_fields = ('name',)

class Alarm_Admin(admin.ModelAdmin):
	filter_horizontal = ('daysOfWeek',)

class UserReport_Admin(admin.ModelAdmin):
	list_display = ('title', 'date', 'user_name', 'email','subscription', 'state', 'working_state')
	search_fields = ('title','user_name', 'email', 'subscription__name', 'state', 'working_state')

class Triggeredalarm_Admin(admin.ModelAdmin):
	list_display = ('alarm', 'state')

class Note_Admin(admin.ModelAdmin):
	list_display = ('name','state', 'user')
	search_fields = ('name', 'state','user__username')

class Localization_Admin(admin.ModelAdmin):
	list_display = ('lat', 'lon', 'address')
	search_fields = ('lat', 'lon', 'address')

class Alarm_Admin(admin.ModelAdmin):
	list_display = ('name', 'type_alarm', 'threshold', 'state', 'user')
	search_fields = ('name', 'type_alarm', 'threshold', 'state', 'user')

admin.site.unregister(Group)
admin.site.unregister(TaskResult)
admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(FCMDevice)

admin.site.register(Sensor, Sensor_Admin)
admin.site.register(Subscription, Subscription_Admin)
admin.site.register(UserReport, UserReport_Admin)
admin.site.register(Value, Value_Admin)
admin.site.register(Note, Note_Admin)
admin.site.register(Alarm, Alarm_Admin)
admin.site.register(AlarmActuator)
admin.site.register(Subscription_Group, Subscription_Group_Admin)
#admin.site.register(day_year)
#admin.site.register(day_week)
admin.site.register(Triggered_alarm, Triggeredalarm_Admin)
admin.site.register(Localization, Localization_Admin)
admin.site.register(ReportAttach)