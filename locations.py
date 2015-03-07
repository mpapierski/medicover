import json
import sys
import re

import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim

session = requests.Session()
geolocator = Nominatim()

def fix_cityname(cityname):
    """XX-YYY City -> ('xx-yyy', 'city')
    """
    m = re.match(r'^(\d{2}-\d{3}) (.*)$', cityname)
    try:
        zip_code, cityname = m.groups()
        return zip_code, cityname
    except (AttributeError, ValueError):
        return None, cityname

def get_viewstate(content):
    """Extracts __VIEWSTATE magic value
    """
    bs = BeautifulSoup(content)
    return bs.select('form#form1 input[name=__VIEWSTATE]')[0]['value']

def extract_data(url):
    r = session.get(url)
    r.raise_for_status()
    bs = BeautifulSoup(r.content)
    result = {}
    address = bs.select('span#ctrl_522_lblAddress')[0].text
    result['address'] = address
    zip_code, cityname = fix_cityname(bs.select('span#ctrl_522_lblCityName')[0].text)
    result['zip_code'] = zip_code
    result['cityname'] = cityname

    # Get lat/long using openstreetmap.org
    geocode_address = u'{0}, {1}'.format(address, cityname)
    location = geolocator.geocode(geocode_address)

    result['geocode'] = None
    if location is not None:
        result['geocode'] = {
            'address': location.address,
            'geo': [location.latitude, location.longitude]
        }
    return result

def get_locations():
    r = session.get('http://www.medicover.pl/274,placowki-medyczne.htm')
    r.raise_for_status()
    viewstate = get_viewstate(r.content)
    current_page = 1


    headers = {
        'X-MicrosoftAjax': 'Delta=false',
        'X-Requested-With':'XMLHttpRequest'
    }
    while True:
        r = session.post('http://www.medicover.pl/274,placowki-medyczne.htm',
            data={
                'ScriptManager_HiddenField': 'ctrl_522$ctl01$upRefreshMap|ctrl_522$ctl01$gvSearch',
                '__EVENTTARGET': 'ctrl_522$ctl01$gvSearch',
                '__EVENTARGUMENT': 'Page${0}'.format(current_page),
                '__LASTFOCUS': '',
                '__VIEWSTATE': viewstate,
                '__VIEWSTATEGENERATOR': 'CA0B0334',
                '__VIEWSTATEENCRYPTED': '',
                'ctl10$tbxSearch': '',
                'ctrl_522$ctl01$tbxCityName': '',
                'ctrl_522$ctl01$tbxStreet': '',
                'ctrl_522$ctl01$ctl03$tbxMapType': '',
                'ctrl_522$ctl01$ctl03$tbxZoom': '6',
                'ctrl_522$ctl01$ctl03$tbxMarkers': '',
                'ctrl_522$ctl01$ctl03$tbxDate': '',
                'ctrl_522$ctl01$ctl03$tbxBounds': '',
                'ctrl_522$ctl01$ctl03$tbxLocalizationTypeId': '2',
            },
            headers=headers)
        r.raise_for_status()
        bs = BeautifulSoup(r.content)

        with open('placowki{0}.html'.format(current_page), 'wb') as f:
           f.write(r.content)
           #sys.exit(1)

        for el in bs.select('a.mcovLocalization'):
            yield (el.text, el['href'])

        # Next pages
        next_page = None
        for el in bs.select('a[href^="javascript:__doPostBack(\'ctrl_522$ctl01$gvSearch\',\'Page"]'):
            next_page = max(next_page, int(el.text))

        if next_page > current_page:
            current_page = next_page
            viewstate = get_viewstate(r.content)
        else:
            break

def main():
    print 'Extracting locations'
    locations = []
    for name, url in get_locations():
        print name
        locations.append([name, url])
    print 'OK ({0})'.format(len(locations))
    print 'Extracting metadata'
    # Reorder (name -> metadata)
    items = {}
    for index, (name, url)in enumerate(locations, 1):
        metadata = extract_data(url)
        items[name] = {
            'cityname': metadata['cityname'],
            'zip_code': metadata['zip_code'],
            'address': metadata['address'],
            'geocode': metadata['geocode']
        }
        print index, name
    with open('locations.json', 'wb') as f:
        json.dump(items, f, indent=4)

if __name__ == '__main__':
    main()