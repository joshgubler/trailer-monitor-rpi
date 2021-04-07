#!/usr/bin/env python3

import gpsd, json, time, util

mode_map = {
    0: 'No mode value seen yet',
    1: 'No fix',
    2: '2D',
    3: '3D',
}

parameters = {
        'alt': { 'gpsd_key': 'alt', 'description': 'Altitude', 'unit': 'meters', 'default': None },
        'alt_err': { 'gpsd_key': 'error', 'gpsd_subkey': 'v', 'description': 'Altitude accuracy', 'unit': 'meters', 'default': None },
        'climb': { 'gpsd_key': 'climb', 'description': 'Climb Rate', 'unit': 'meters/sec', 'default': None },
        'climb_err': { 'gpsd_key': 'error', 'gpsd_subkey': 'c', 'description': 'Climb rate accuracy', 'unit': 'meters/sec', 'default': None },
        'lat': { 'gpsd_key': 'lat', 'description': 'Latitude', 'unit': 'deg', 'default': None },
        'lat_err': { 'gpsd_key': 'error', 'gpsd_subkey': 'y', 'description': 'Latitude accuracy', 'unit': 'meters', 'default': None },
        'lon': { 'gpsd_key': 'lon', 'description': 'Longitude', 'unit': 'deg', 'default': None },
        'lon_err': { 'gpsd_key': 'error', 'gpsd_subkey': 'x', 'description': 'Longitude accuracy', 'unit': 'meters', 'default': None },
        'mode': { 'gpsd_key': 'mode', 'description': 'GPS Mode', 'mapping': mode_map, 'default': 0 },
        'sats': { 'gpsd_key': 'sats', 'description': 'Satelite Count', 'default': 0 },
        'speed': { 'gpsd_key': 'hspeed', 'description': 'Speed', 'unit': 'meters/sec', 'default': None },
        'speed_err': { 'gpsd_key': 'error', 'gpsd_subkey': 's', 'description': 'Speed accuracy', 'unit': 'meters/sec', 'default': None },
        'time': { 'gpsd_key': 'time', 'description': 'Time', 'default': '' },
        'time_err': { 'gpsd_key': 'error', 'gpsd_subkey': 't', 'description': 'Time accuracy', 'unit':'seconds', 'default': None },
        'track': { 'gpsd_key': 'track', 'description': 'Course (true north)', 'unit': 'degrees', 'default': None }
}

gpsd.connect()

def get_location(verbose):
    while True:
        try:
            #print("getting gps data")
            packet = gpsd.get_current()
            if packet.mode >= 2:
                #print("got a fix! continue to parsing")
                break
            else:
                #print("no fix. sleeping")
                time.sleep(1)
        except:
            #print("error getting gps data. sleeping")
            time.sleep(1)
    location = {}
    for key, metadata in parameters.items():
        location[key] = param(metadata, packet, verbose)
    return location

def param(metadata, packet, verbose):
    value = getattr(packet, metadata['gpsd_key'], metadata['default'])
    if 'gpsd_subkey' in metadata:
        value = value[metadata['gpsd_subkey']]
    if 'multiplier' in metadata:
        value = round(float(value)*metadata['multiplier'], 2)
    if 'mapping' in metadata:
        value = metadata['mapping'][value]
    response = {
        'value': value,
        'label': metadata['description']
    }
    if 'unit' in metadata:
        response['unit'] = metadata['unit']
        if response['unit'] == 'meters':
            response['value'] = util.meters_to_feet(response['value'])
            response['unit'] = 'ft'
        if response['unit'] == 'meters/sec':
            response['value'] = util.meters_per_second_to_miles_per_hour(response['value'])
            response['unit'] = 'mph'
    if verbose:
        return response
    else:
        return response['value']

if __name__ == '__main__':
    while True:
        location = get_location(False)
        with open('../data/gps.json', 'w') as f:
            f.write(json.dumps(location))
        time.sleep(1)

