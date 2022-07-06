#!/usr/bin/python3
import time
import calendar
import os
import json
import prometheus_client
import logging
import sys
import evohomeclient
import requests

logging.getLogger().setLevel(logging.DEBUG)

EXPORTER_PORT = 9999
UPDATE_PERIOD = 60
TCC_USERNAME = os.getenv('TCC_USERNAME')
TCC_PASSWORD = os.getenv('TCC_PASSWORD')

THERMOSTAT = prometheus_client.Gauge('tcc_temp',
                                       'device',
                                          [ 'thermostat',
                                            'id', 
                                            'name'
                                          ]
                                    )


def update_temperatures():
    try:
      client = evohomeclient.EvohomeClient(TCC_USERNAME, TCC_PASSWORD)
      temperatures = client.temperatures()
      logging.debug("Setting temps!")
      for device in temperatures:
        logging.debug (device)
        # device_dict = json.loads(device)

        THERMOSTAT.labels(  thermostat=device['thermostat'], 
                            id=device['id'], 
                            name=device['name']
                          ).set(device['temp'])

    except requests.exceptions.HTTPError as errh:
        logging.debug ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        logging.debug ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        logging.debug ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        logging.debug ("OOps: Something Else",err)

if __name__ == '__main__':
    prometheus_client.start_http_server(EXPORTER_PORT)
    my_metrics = {}

    while True:
        logging.debug("Updating Temps, %s", calendar.timegm(time.gmtime()))
        update_temperatures()
        time.sleep(UPDATE_PERIOD)
