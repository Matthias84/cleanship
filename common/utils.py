from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.mail import send_mail
from requests.exceptions import ConnectionError, HTTPError, Timeout
import requests
import json
import logging

logger = logging.getLogger(__name__)

def reverse_geocode(point):
    """
    calling webservice to get string description of position
    currently hardcoded against geocodr service (https://geo.sv.rostock.de/geocodr.html)
    """
    lat, lon = point.coords
    url = 'https://geo.sv.rostock.de/geocodr/query?key=' + settings.GEOCODR_API_KEY
    searchdist = "50"
    payload = {"type": "reverse", "class": "address", "query": str(lat)+","+str(lon), "radius": searchdist, "in_epsg": "4326"}
    headers = {'content-type': 'application/json'}
    result = None
    try:
        logger.debug("Lookup geocodr ({})".format(url))
        r = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5.0)
        #r.status_code == requests.codes.ok
        features = r.json()["features"]
        if len(features) == 0:
            logger.warning("Fail geocoding -  No close features to ({}) within {}m".format(str(point.coords), searchdist))
        else:
            logger.debug("Checking {} features".format(len(features)))
            for feat in features:
                if feat['properties']['objektgruppe'] == 'Adresse':
                    # try first adress
                    logger.debug("Address feature found")
                    street = feat['properties']['strasse_name']
                    number = feat['properties']['hausnummer']
                    addon =  feat['properties']['hausnummer_zusatz']
                    if addon == None:
                        addon = ''
                    result ='{} {}{}'.format(street, number, addon)
                    return result
    except ConnectionError:
        logger.warning("Fail geocoding -  Connection error")
    except HTTPError:
        logger.warning("Fail geocoding -  HTTPError")
    except Timeout:
        logger.warning("Fail geocoding -  Timeout")
    except KeyError:
        logger.warning("Fail geocoding -  JSON Key features not found")
    return result
    # TODO: Add district abbreviation

def get_landowner(point):
    """Check if map point is within boundary"""
    # TODO: Extract validators, switch datasource #56
    point.transform(25833) # TODO: django gis docs say autoconvert?
    logger.info("Loading landowner polygons")
    ds = DataSource('eigentumsangaben.geojson')
    layer = ds[0]
    logger.info("Checking {} landowner polygons".format(len(layer)))
    for feature in layer:
        poly = feature.geom.geos
        if poly.contains(point) == True:
            owner = feature.get('eigentumsangabe')
            logger.info("Found point in polygon id {} ({})".format(feature.get('id'), owner)) #TODO: provide more characteristics?
            return owner
    logger.warning("Fail landowner - No polygon for ({})".format(str(point.coords)))
    return None
    
def send_author_email_notification(issue):
    '''Send UTF-8 encoded mail '''
    # TODO: We need better formating, templates, inheritance, ...
    logger.info("Send email notification")
    send_mail(
        '🌟Klarschiff.HRO #{} erstellt'.format(issue.id),
        'Für Sie wurde eine neue Meldung mit folgendem Inhalt erstellt: "{}"'.format(issue.description),
        settings.EMAIL_FROM,
        [issue.author_email],
        fail_silently=False,)
