#!/usr/bin/env python3
import json

def read_location():
    location = None
    with open('../data/gps.json') as f:
        location = f.read()
    location = json.loads(location) if location else None
    return location

def read_power():
    power = None
    with open('../data/power.json') as f:
        power = f.read()
    power = json.loads(power) if power else None
    return power

def combine_data():
    return { 'location': read_location(), 'power': read_power() }

def celsius_to_fahrenheit(value):
    if value is None:
        return None
    return value*9/5+32

def meters_to_feet(value):
    if value is None:
        return None
    return value*3.28084

def meters_per_second_to_miles_per_hour(value):
    if value is None:
        return None
    return value*2.2369363

