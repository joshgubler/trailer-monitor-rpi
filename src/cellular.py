#!/usr/bin/env python3

import json, time, requests

def get_cellular():
    cellular = requests.get('https://192.168.4.1/cgi-bin/insty/getcsq', verify=False)
    return cellular.json()

if __name__ == '__main__':
    while True:
        cellular = get_cellular()
        with open('../data/cellular.json', 'w') as f:
            f.write(json.dumps(cellular))
        time.sleep(2)

