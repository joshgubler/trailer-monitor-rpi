#!/usr/bin/env python3

from datetime import datetime
import json, time, util

if __name__ == '__main__':
    while True:
        data = util.combine_data()
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        with open(f'../data/{timestamp}.json', 'w') as f:
            f.write(json.dumps(data))
        time.sleep(60)

