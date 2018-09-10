from django.forms.extras.widgets import SelectDateWidget
import datetime
from django import forms
from models import Alarm


class ChoiceFieldNoValidation(forms.MultipleChoiceField):
	def validate(self, value):
		pass


class ActuatorForm(forms.Form):

	def __init__(self, *args, **kwargs):
		try:
			senders = kwargs.pop('senders')
			super(forms.Form, self).__init__(*args, **kwargs)
			self.fields['streams'].choices = senders
			super(ActuatorForm, self).full_clean()
		except Exception as e:
			super(forms.Form, self).__init__(*args, **kwargs)


	streams = ChoiceFieldNoValidation(widget=forms.CheckboxSelectMultiple)
	value = forms.FloatField(initial=0, required=True)

	def clean(self):
		cleaned_data = super(ActuatorForm, self).clean()

		if len(cleaned_data['streams'])==0:
			raise forms.ValidationError("Select at least one stream")

		return cleaned_data

class RuleForm(forms.Form):
	def __init__(self, *args, **kwargs):
		try:
			senders = kwargs.pop('senders')
			super(forms.Form, self).__init__(*args, **kwargs)
			self.fields['streams'].choices = senders
			super(RuleForm, self).full_clean()
		except Exception as e:
			super(forms.Form, self).__init__(*args, **kwargs)
	
	
	beg_date = forms.DateField(widget=SelectDateWidget, initial=datetime.date.today)
	end_date = forms.DateField(widget=SelectDateWidget, initial=datetime.date.today)

	name = forms.CharField(max_length=50, required=True)

	mo = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'weekday','id':'weekday-mon2','type':'checkbox'}), initial=False, required=False)
	tu = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'weekday','id':'weekday-tue2','type':'checkbox'}), initial=False, required=False)
	we = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'weekday','id':'weekday-wed2','type':'checkbox'}), initial=False, required=False)
	th = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'weekday','id':'weekday-thu2','type':'checkbox'}), initial=False, required=False)
	fr = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'weekday','id':'weekday-fri2','type':'checkbox'}), initial=False, required=False)
	sa = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'weekday','id':'weekday-sat2','type':'checkbox'}), initial=False, required=False)
	su = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'weekday','id':'weekday-sun2','type':'checkbox'}), initial=False, required=False)

	streams = ChoiceFieldNoValidation(widget=forms.CheckboxSelectMultiple)
	value = forms.FloatField(initial=0, required=True)

	beg_hour = forms.IntegerField(max_value=23, min_value=0)
	beg_min = forms.IntegerField(max_value=59, min_value=0)

	end_hour = forms.IntegerField(max_value=23, min_value=0)
	end_min = forms.IntegerField(max_value=59, min_value=0)

	hours_active_beg = forms.IntegerField(max_value=23, min_value=0)
	minutes_active_beg = forms.IntegerField(max_value=59, min_value=0)

	def clean(self):
		cleaned_data = super(RuleForm, self).clean()

		beg_date = cleaned_data['beg_date']
		end_date = cleaned_data['end_date']

		beg_hour = cleaned_data['beg_hour']
		end_hour = cleaned_data['end_hour']

		beg_min = cleaned_data['beg_min']
		end_min = cleaned_data['end_min']

		if beg_date > end_date or (beg_date == end_date and beg_hour > end_hour) or (beg_date == end_date and beg_hour == end_hour and beg_min>end_min):
			raise forms.ValidationError("Turn on date should be before turn off date.")

		if len(cleaned_data['streams'])==0:
			raise forms.ValidationError("Select at least one stream")

		return cleaned_data

class AlarmForm(forms.Form):

	def __init__(self, *args, **kwargs):
		try:
			subscription_list = kwargs.pop('subscriptions')
			super(forms.Form, self).__init__(*args, **kwargs)
			self.fields['subscriptions'].choices = subscription_list
			super(AlarmForm, self).full_clean()
		except Exception as e:
			super(forms.Form, self).__init__(*args, **kwargs)
	
	
	beg_date = forms.DateField(widget=SelectDateWidget, initial=datetime.date.today)
	end_date = forms.DateField(widget=SelectDateWidget, initial=datetime.date.today)

	name = forms.CharField(max_length=50, required=True)

	mo = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'weekday','id':'weekday-mon','type':'checkbox'}), initial=False, required=False)
	tu = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'weekday','id':'weekday-tue','type':'checkbox'}), initial=False, required=False)
	we = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'weekday','id':'weekday-wed','type':'checkbox'}), initial=False, required=False)
	th = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'weekday','id':'weekday-thu','type':'checkbox'}), initial=False, required=False)
	fr = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'weekday','id':'weekday-fri','type':'checkbox'}), initial=False, required=False)
	sa = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'weekday','id':'weekday-sat','type':'checkbox'}), initial=False, required=False)
	su = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'weekday','id':'weekday-sun','type':'checkbox'}), initial=False, required=False)

	threshold = forms.FloatField()

	beg_hour = forms.IntegerField(max_value=23, min_value=0)
	beg_min = forms.IntegerField(max_value=59, min_value=0)

	end_hour = forms.IntegerField(max_value=23, min_value=0)
	end_min = forms.IntegerField(max_value=59, min_value=0)

	hours_active_beg = forms.IntegerField(max_value=23, min_value=0)
	minutes_active_beg = forms.IntegerField(max_value=59, min_value=0)
	hours_active_end = forms.IntegerField(max_value=23, min_value=0)
	minutes_active_end = forms.IntegerField(max_value=59, min_value=0)

	subscriptions = ChoiceFieldNoValidation(widget=forms.CheckboxSelectMultiple, required=True)
	type_alarm = forms.ChoiceField(choices=(('MAX', 'Maximum'), ('MIN', 'Minimum'), ), widget=forms.RadioSelect)

	def clean(self):
		cleaned_data = super(AlarmForm, self).clean()

		beg_date = cleaned_data['beg_date']
		end_date = cleaned_data['end_date']

		beg_hour = cleaned_data['beg_hour']
		end_hour = cleaned_data['end_hour']

		beg_min = cleaned_data['beg_min']
		end_min = cleaned_data['end_min']

		if len(cleaned_data['subscriptions'])==0:
			raise forms.ValidationError("Select at least one subscription")

		if beg_date > end_date or (beg_date == end_date and beg_hour > end_hour) or (beg_date == end_date and beg_hour == end_hour and beg_min>end_min):
			raise forms.ValidationError("Turn on date should be before turn off date.")

		return cleaned_data

class NoteForm(forms.Form):
	title = forms.CharField()
	message = forms.CharField(widget=forms.Textarea, max_length=250)

	beg_date = forms.DateField(widget=SelectDateWidget, initial=datetime.date.today)
	hours_beg = forms.IntegerField(max_value=23, min_value=0)
	minutes_beg = forms.IntegerField(max_value=59, min_value=0)

	end_date = forms.DateField(widget=SelectDateWidget, initial=datetime.date.today)
	hours_end = forms.IntegerField(max_value=23, min_value=0)
	minutes_end = forms.IntegerField(max_value=59, min_value=0)

	def clean(self):
		cleaned_data = super(NoteForm, self).clean()

		beg_date = cleaned_data['beg_date']
		end_date = cleaned_data['end_date']

		beg_hour = cleaned_data['hours_beg']
		end_hour = cleaned_data['minutes_beg']

		beg_min = cleaned_data['hours_end']
		end_min = cleaned_data['minutes_end']


		if beg_date > end_date or (beg_date == end_date and beg_hour > end_hour) or (beg_date == end_date and beg_hour == end_hour and beg_min>end_min):
			raise forms.ValidationError("Turn on date should be before turn off date.")

		return cleaned_data

