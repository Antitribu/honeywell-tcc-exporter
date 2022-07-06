#!/usr/bin/python3
import time
import calendar
import os
import prometheus_client
import logging
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

SETPOINT = prometheus_client.Gauge('tcc_setpoint',
                                       'device',
                                          [ 'thermostat',
                                            'id', 
                                            'name'
                                          ]
                                    )

STATUS = prometheus_client.Gauge('tcc_states',
                                       'device',
                                          [ 'thermostat',
                                            'id', 
                                            'name',
                                            'status'
                                          ]
                                    )

MODE = prometheus_client.Gauge('tcc_mode',
                                       'device',
                                          [ 'thermostat',
                                            'id', 
                                            'name',
                                            'mode'
                                          ]
                                    )


HTTP_RESPONSE = prometheus_client.Counter('tcc_http_response', "HTTP Responses", ['type'])

def update_temperatures(metrics_dict):
    try:
      client = evohomeclient.EvohomeClient(TCC_USERNAME, TCC_PASSWORD)
      temperatures = client.temperatures()
      logging.debug("Setting temps!")
      for device in temperatures:
        logging.debug (device)

        THERMOSTAT.labels(  thermostat=device['thermostat'], 
                            id=device['id'], 
                            name=device['name']
                          ).set(device['temp'])

        SETPOINT.labels(  thermostat=device['thermostat'], 
                            id=device['id'], 
                            name=device['name']
                          ).set(device['setpoint'])

        if device['status'] not in metrics_dict['status']:
          metrics_dict['status'].append(device['status'])
          logging.debug (metrics_dict)
        
        for status_zero in metrics_dict['status']:
          logging.debug (status_zero)
          STATUS.labels(  thermostat=device['thermostat'], 
                              id=device['id'], 
                              name=device['name'],
                              status=status_zero
                            ).set(0)

        STATUS.labels(  thermostat=device['thermostat'], 
                            id=device['id'], 
                            name=device['name'],
                            status=device['status']
                          ).set(1)

        if device['mode'] not in metrics_dict['mode']:
          metrics_dict['mode'].append(device['mode'])
          logging.debug (metrics_dict)
        
        for mode_zero in metrics_dict['mode']:
          logging.debug (mode_zero)
          MODE.labels(  thermostat=device['thermostat'], 
                              id=device['id'], 
                              name=device['name'],
                              mode=mode_zero
                            ).set(0)

        MODE.labels(  thermostat=device['thermostat'], 
                            id=device['id'], 
                            name=device['name'],
                            mode=device['mode']
                          ).set(1)

    except requests.exceptions.HTTPError as errh:
        logging.debug ("Http Error:",errh)
        HTTP_RESPONSE.labels(type="HTTPError_Total").inc(1)
        HTTP_RESPONSE.labels(type=(str(errh).split(', ')[0].rsplit(' ', maxsplit=1)[1])).inc(1)
    except requests.exceptions.ConnectionError as errc:
        logging.debug ("Error Connecting:",errc)
        HTTP_RESPONSE.labels(type="ConnectionError").inc(1)
    except requests.exceptions.Timeout as errt:
        logging.debug ("Timeout Error:",errt)
        HTTP_RESPONSE.labels(type="Timeout").inc(1)
    except requests.exceptions.RequestException as err:
        logging.debug ("Oops: Something Else",err)
        HTTP_RESPONSE.labels(type="Other").inc(1)

    return metrics_dict


if __name__ == '__main__':
    prometheus_client.start_http_server(EXPORTER_PORT)
    my_metrics = {}
    my_metrics['status'] = []
    my_metrics['mode'] = []

    while True:
        logging.debug("Updating Temps, %s", calendar.timegm(time.gmtime()))
        update_temperatures(my_metrics)
        time.sleep(UPDATE_PERIOD)
