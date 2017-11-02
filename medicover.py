import json
import os
import requests
import HTMLParser
from bs4 import BeautifulSoup

username = os.environ['MEDICOVER_USERNAME']
password = os.environ['MEDICOVER_PASSWORD']

session = requests.Session()

# Step 1: Open login page.
r = session.get('https://mol.medicover.pl/Users/Account/LogOn')
bs = BeautifulSoup(r.content)
json_text = HTMLParser.HTMLParser().unescape(bs.select('#modelJson')[0].text)
token = json.loads(json_text)['antiForgery']['value']

# Step 2: Send login info.
r = session.post(
    r.url,
    data={
			'username': username,
			'password': password,
			'idsrv.xsrf': token,
    })
r.raise_for_status()
bs = BeautifulSoup(r.content)

def getHiddenField(name):
  return bs.select('input[name="%s"]' % name)[0]['value']

# Step 3: Forward auth info to main page.
r = session.post(
	'https://mol.medicover.pl/Medicover.OpenIdConnectAuthentication/Account/OAuthSignIn',
	data={
		'code': getHiddenField('code'),
		'id_token': getHiddenField('id_token'),
		'scope': getHiddenField('scope'),
		'state': getHiddenField('state'),
		'session_state': getHiddenField('session_state'),
	})
r.raise_for_status()

all_appointments = []

page = 1
while True:
	pageSize = 12

	r = session.post('https://mol.medicover.pl/api/MyVisits/SearchVisitsToView',
		headers={
			'X-Requested-With': 'XMLHttpRequest'
		},
		data={
			'Page': page,
			'PageSize': pageSize,
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
