# encoding: utf-8
import os
import requests
import json
import datetime
import warnings
import functools
import operator
from requests.packages.urllib3 import exceptions
import pytz
import dateutil.parser
import caldav
from caldav.elements import dav, cdav
from icalendar import Calendar, Event, vText, vDatetime
from difflib import SequenceMatcher

from fuzzywuzzy import fuzz

# Ignore SSL errors

old_request = requests.request

#@functools.wraps(old_request)
def new_request(*args, **kwargs):
	kwargs['verify'] = False
	with warnings.catch_warnings():
		warnings.simplefilter("ignore", exceptions.InsecureRequestWarning)
		return old_request(*args, **kwargs)

requests.request = new_request

###
url = os.environ['CALDAV_URL']

now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


def get_location(req):
	"""Reads locations.json and makes key lookupable by clinicName
	"""
	# Expand some tokens
	req = 'Centrum Medicover ' + req
	req = req.replace(u'Płd.', u'Południe')
	req = req.replace(' CM ', ' ')
	
	# Expand `req`
	with open('locations.json') as f:
		locations = json.load(f)
		matches = []
		for key, value in locations.items():
			# Expand key
			if value:
				expanded_key = u'{0} {1}'.format(key, value['cityname'])
			else:
				expanded_key = key
			ratio = fuzz.partial_ratio(req.lower(), expanded_key.lower())
			matches.append([key, ratio])
		matches.sort(key=operator.itemgetter(1))
		lookup_key, ratio = matches[-1]
		return locations[lookup_key]

def main():

	appointments = None

	with open('appointments.json') as f:
		appointments = json.load(f)

	# Generate vcal events from appointments
	icalendars = []

	for appointment in appointments:
		cal = Calendar()
		location = get_location(appointment['clinicName'])
		dt = dateutil.parser.parse(appointment['appointmentDate'])
		tz = pytz.timezone('Europe/Warsaw')
		local = dt.replace(tzinfo=tz)
		event = Event()
		#event['methdo']
		event['uid'] = '{0}@medicover.pl'.format(appointment['id'])
		event['dtstart'] = vDatetime(local)
		event['dtend'] = vDatetime(local + datetime.timedelta(hours=1))
		event['dtstamp'] = vDatetime(now)
		event['summary'] = vText(appointment['specializationName'])
		event['description'] = vText(u'{0}, {1}'.format(
			appointment['specializationName'], appointment['doctorName']))
		event['class'] = 'private'

		if location:
			event['location'] = vText(u'{0}, {1}'.format(location['address'], location['cityname']))
			geocode = location['geocode']
			if geocode:
				event['geo'] = '{0};{1}'.format(*geocode['geo'])
		else:
			event['location'] = appointment['clinicName']
			
		cal.add_component(event)
		icalendars.append(cal)

	#print cal.to_ical()

	
	client = caldav.DAVClient(url)
	principal = client.principal()
	calendars = principal.calendars()

	for calendar in calendars:
		name = calendar.get_properties([dav.DisplayName(),])['{DAV:}displayname']
		if name == 'Medicover':
			for cal in icalendars:
				print cal.to_ical()
				event = calendar.add_event(cal.to_ical())
				print 'Event', event, 'created'

	#for appointment in appointments:
		#print appointment['doctorName']
		#appointmentDate = dateutil.parser.parse(appointment['appointmentDate'])
		#print appointment['appointmentDate'], appointmentDate

if __name__ == '__main__':
	main()
