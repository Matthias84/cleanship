from django.conf import settings
from requests.exceptions import ConnectionError, HTTPError, Timeout
import requests
import json

def reverse_geocode(point):
    """
    calling webservice to get string description of position
    currently hardcoded against 
    """
    lat, lon = point.coords
    url = 'https://geo.sv.rostock.de/geocodr/query?key=' + settings.GEOCODR_API_KEY
    payload = {"type": "reverse", "class": "address", "query": str(lat)+","+str(lon), "radius": "50", "in_epsg": "4326"}
    headers = {'content-type': 'application/json'}
    result = None
    try:
        r = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5.0)
        #r.status_code == requests.codes.ok
        features = r.json()["features"]
        for feat in features:
            if feat['properties']['objektgruppe'] == 'Adresse':
                # try first adress
                street = feat['properties']['strasse_name']
                number = feat['properties']['hausnummer']
                addon =  feat['properties']['hausnummer_zusatz']
                if addon == None:
                    addon = ''
                result ='%s %s%s' % (street, number, addon)
                return result
    except ConnectionError:
        pass
    except HTTPError:
        pass
    except Timeout:
        pass
        # TODO: Log useful details on failed connection
    return result
    # try district abbreviation

