"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import TemplateView
from mainserver import views
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from fcm_django.api.rest_framework import FCMDeviceViewSet
    

urlpatterns = [
	
    url(r'^(success=(?P<success>True|False))?$', views.index),
    url(r'^login/$', auth_views.login, {'template_name': 'adminlte/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/login'}, name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^map/$', views.map),
    url(r'^temperature/(days=(?P<days>[0-9]+)/)?(weeks=(?P<weeks>[0-9]+)/)?(hours=(?P<hours>[0-9]+)/)?$', views.temperature),
    url(r'^lighting/(days=(?P<days>[0-9]+)/)?(weeks=(?P<weeks>[0-9]+)/)?(hours=(?P<hours>[0-9]+)/)?$', views.lighting),
    url(r'^air/(days=(?P<days>[0-9]+)/)?(weeks=(?P<weeks>[0-9]+)/)?(hours=(?P<hours>[0-9]+)/)?$', views.air),
    url(r'^waste/(days=(?P<days>[0-9]+)/)?(weeks=(?P<weeks>[0-9]+)/)?(hours=(?P<hours>[0-9]+)/)?$', views.waste),
    url(r'^noise/(days=(?P<days>[0-9]+)/)?(weeks=(?P<weeks>[0-9]+)/)?(hours=(?P<hours>[0-9]+)/)?$', views.noise),
    url(r'^radiation/(days=(?P<days>[0-9]+)/)?(weeks=(?P<weeks>[0-9]+)/)?(hours=(?P<hours>[0-9]+)/)?$', views.radiation),
    url(r'^people/(days=(?P<days>[0-9]+)/)?(weeks=(?P<weeks>[0-9]+)/)?(hours=(?P<hours>[0-9]+)/)?$', views.people),
    url(r'^alerts/(success=(?P<success>True|False|Trueactuator|Falseactuator))?$', views.alerts),
    url(r'^alerts/(?P<s_id>[A-Za-z0-9._;,-]+)(/(success=(?P<success>True|False|Trueactuator|Falseactuator))?)/addActuator/(?P<alertId>[0-9]+)$', views.add_actuator_alert),
    url(r'^alerts/info/([0-9]+)$', views.info_alert),
    url(r'^alerts/details/(?P<id>[0-9]+)(/(success=(?P<success>True|False|Trueactuator|Falseactuator))?)$', views.alert_details),
    url(r'^alerts/triginfo/(?P<id>[0-9]+)$', views.info_triggered),
    url(r'^alerts/triginfo$', views.info_trigalerts),
    url(r'^alerts/id=(?P<id>[0-9]+)$', views.alerts),
    url(r'^help/$', views.help),
    url(r'^sensors/details/(?P<s_id>[A-Za-z0-9._;,-]+)(/success=(?P<success>True|False|Trueactuator|Falseactuator|TrueRule|FalseRule))?$', views.details),
    url(r'^sensors/details/(?P<s_id>[A-Za-z0-9._;,-]+)((/success=(?P<success>True|False|Trueactuator|Falseactuator|TrueRule|FalseRule))?)/addActuator/(?P<alertId>[0-9]+)$', views.add_actuator),
    url(r'^sensors/details/(?P<s_id>[A-Za-z0-9._;,-]+)((/success=(?P<success>True|False|Trueactuator|Falseactuator|TrueRule|FalseRule))?)/addRule$', views.add_rule),
    url(r'^addActuator/(?P<alertId>[0-9]+)$',views.add_actuator2),
    url(r'^sensors/(on|off)/([A-Za-z0-9._;,-]+)$', views.change_sensor),
    url(r'^sensors/send/([A-Za-z0-9._;,-]+)/([A-Za-z0-9._;,-]+)$', views.send_value),
    url(r'^note/delete/([0-9]+)$', views.delete_note),
    url(r'^note/info/([0-9]+)$', views.info_note),
    url(r'^note/add$', views.add_note),
    url(r'^reports/$', views.reports),
    url(r'^alerts/delete/(?P<id>[0-9]+)/sub=(?P<sub>[A-Za-z0-9._;,-]+)$', views.deleteStreamFromAlert),
    url(r'^alerts/deleteTrig/(?P<id>[0-9]+)/sen=(?P<sen>[A-Za-z0-9._;,-]+)$', views.deleteTrigAlert),
    url(r'^rules/(success=(?P<success>True|False|Trueactuator|Falseactuator))?$', views.rules),
    url(r'^rules/details/(?P<id>[0-9]+)/(success=(?P<success>True|False|Trueactuator|Falseactuator))?$', views.rule_details),
    url(r'^rules/addActuator/(?P<s_id>[A-Za-z0-9._;,-]+)$', views.addActuatorToRule),
    url(r'^reports/delete/id=([0-9]+)$', views.delete_report),
    url(r'^reports/getAttach/id=([0-9]+)$', views.get_document),
    url(r'^reports/read/id=([0-9]+)$', views.read_report),
    url(r'^reports/state/(?P<id>[0-9]+)/(?P<state>NS|SE)$', views.change_state_report),
    url(r'^reports/workingstate/(?P<id>[0-9]+)/(?P<state>WA|WI|SO)$', views.change_working_state_report),
    url(r'^alerts/state/(?P<id>[0-9]+)/(?P<state>AC|NS|SE)$', views.change_state_TrigAlert),
    url(r'^alerts/delete/(?P<id>[0-9]+)$', views.delete_alert),
    url(r'^trigg/delete/(?P<id>[0-9]+)$', views.delete_TrigAlert),
    url(r'^actuator/delete/(?P<id>[0-9]+)/sub=(?P<sub_id>[A-Za-z0-9._;,-]+)$', views.delete_actuator),
    url(r'^mobile/dashboard/(?P<lat>[-+]?\d{1,2}[.]\d+)/(?P<lon>[-+]?\d{1,3}[.]\d+)$',views.mobile_index),
    url(r'^mobile/map/$', views.mobile_map),
    url(r'^mobile/temperature/(days=(?P<days>[0-9]+)/)?(weeks=(?P<weeks>[0-9]+)/)?(hours=(?P<hours>[0-9]+)/)?$', views.mobile_temperature),
    url(r'^mobile/lighting/(days=(?P<days>[0-9]+)/)?(weeks=(?P<weeks>[0-9]+)/)?(hours=(?P<hours>[0-9]+)/)?$', views.mobile_lighting),
    url(r'^mobile/air/(days=(?P<days>[0-9]+)/)?(weeks=(?P<weeks>[0-9]+)/)?(hours=(?P<hours>[0-9]+)/)?$', views.mobile_air),
    url(r'^mobile/waste/(days=(?P<days>[0-9]+)/)?(weeks=(?P<weeks>[0-9]+)/)?(hours=(?P<hours>[0-9]+)/)?$', views.mobile_waste),
    url(r'^mobile/noise/(days=(?P<days>[0-9]+)/)?(weeks=(?P<weeks>[0-9]+)/)?(hours=(?P<hours>[0-9]+)/)?$', views.mobile_noise),
    url(r'^mobile/radiation/(days=(?P<days>[0-9]+)/)?(weeks=(?P<weeks>[0-9]+)/)?(hours=(?P<hours>[0-9]+)/)?$', views.mobile_radiation),
    url(r'^mobile/people/(days=(?P<days>[0-9]+)/)?(weeks=(?P<weeks>[0-9]+)/)?(hours=(?P<hours>[0-9]+)/)?$', views.mobile_people),
    url(r'^ws/addsensor$',views.add_sensor),
    url(r'^ws/addsubscription$',views.add_subscription),
    url(r'^getNewSensors$',views.newSensors),
    url(r'^mobile/report$',views.mobile_report),
    url(r'^devices/$', FCMDeviceViewSet.as_view({'post': 'create'}), name='create_fcm_device'),

]

