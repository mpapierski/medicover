import os
import requests
from bs4 import BeautifulSoup
import json

username = os.environ['MEDICOVER_USERNAME']
password = os.environ['MEDICOVER_PASSWORD']

headers = {'User-Agent': 'Mozilla/5.0'}
payload = {
	'userNameOrEmail': username,
	'password': password,
}

session = requests.Session()

# Get verification token
r = session.get('https://mol.medicover.pl/')
r.raise_for_status()
bs = BeautifulSoup(r.content)

verification_token = bs.select('input[name="__RequestVerificationToken"]')[0]['value']

r = session.post('https://mol.medicover.pl/Users/Account/LogOn?ReturnUrl=%2F',
	data={
		'userNameOrEmail': username,
		'password': password,
		'__RequestVerificationToken': verification_token
	})
r.raise_for_status()

all_appointments = []

page = 1
while True:
	pageSize = 12

	r = session.get('https://mol.medicover.pl/api/MyVisits/SearchVisitsToView',
		headers={
			'X-Requested-With': 'XMLHttpRequest'
		},
		params={
			'appointmentType': None,
			'clinicId': None,
			'doctorId': None,
			'regionId': None,
			'specializationId': None,
			'page': page,
			'pageSize': pageSize,
			'linkFactory': 'undefined'
		})
	r.raise_for_status()

	json_data = r.json()
	all_appointments += json_data['items']
	print len(all_appointments), json_data['totalCount']
	if len(all_appointments) < json_data['totalCount']:
		page += 1
	else:
		break

r = session.get('https://mol.medicover.pl/Users/Account/LogOff')
r.raise_for_status()

with open('appointments.json', 'wb') as f:
	json.dump(all_appointments, f, indent=4)
