from __future__ import absolute_import
from celery import shared_task
import requests

@shared_task
def send_data(url, payload):
	requests.post(url, data = payload)
