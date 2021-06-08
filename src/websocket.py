#!/usr/bin/env python3

import os, util, json, asyncio, websockets

SESSIONS = set()
cached_timestamps = {}

def location_event():
    return json.dumps({ 'type': 'location', 'location' : util.read_location() })

def power_event():
    return json.dumps({ 'type': 'power', 'power' : util.read_power() })

def cellular_event():
    return json.dumps({ 'type': 'cellular', 'cellular' : util.read_cellular() })

async def broadcast_message(message):
    if SESSIONS:
        await asyncio.wait([asyncio.create_task(session.send(message)) for session in SESSIONS])

async def broadcast_location():
    await broadcast_message(location_event())

async def broadcast_power():
    await broadcast_message(power_event())

async def broadcast_cellular():
    await broadcast_message(cellular_event())

async def register(websocket):
    SESSIONS.add(websocket)

async def unregister(websocket):
    SESSIONS.remove(websocket)

async def server(websocket, path):
    await register(websocket)
    try:
        await websocket.send(location_event())
        await websocket.send(power_event())
        await websocket.send(cellular_event())
        async for message in websocket:
            pass
    finally:
        await unregister(websocket)

async def monitor_file(filepath, on_change, interval):
    while True:
        timestamp = os.stat(filepath).st_mtime
        if filepath in cached_timestamps and cached_timestamps[filepath] != timestamp:
            await on_change()
        cached_timestamps[filepath] = timestamp
        await asyncio.sleep(interval)

async def main():
    await asyncio.gather(
            websockets.serve(server, "0.0.0.0", 8765),
            monitor_file('../data/gps.json', broadcast_location, 1),
            monitor_file('../data/power.json', broadcast_power, 1),
            monitor_file('../data/cellular.json', broadcast_cellular, 1)
          )

if __name__ == '__main__':
    asyncio.run(main())
