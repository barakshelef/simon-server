#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import os

import websockets

GAMES = dict()


async def notify(message, path):
    loop = asyncio.get_event_loop()
    tasks = set()
    for user in GAMES.get(path, set()):
        tasks.add(loop.create_task(user.send(message)))

    if tasks:
        await asyncio.wait(tasks)


async def notify_users(game_id):
    await notify(json.dumps({"type": "users", "count": len(GAMES[game_id])}), game_id)


async def register(websocket, game_id):
    if game_id not in GAMES:
        print(f"Created new game {game_id}")
        GAMES[game_id] = list()

    player_id = len(GAMES[game_id])
    GAMES[game_id].append(websocket)
    print(f"Registered {game_id} player {player_id}")
    await notify_users(game_id)
    return player_id


async def unregister(websocket, game_id):
    print(f"Player {GAMES[game_id].index(websocket)} left game {game_id}")
    GAMES[game_id].remove(websocket)

    if not GAMES[game_id]:
        print(f"All players left {game_id}, closing.")
        del GAMES[game_id]
    else:
        await notify_users(game_id)


async def relay(websocket, path):
    # register(websocket) sends user_event() to websocket
    game_id = path[1:]
    user_id = await register(websocket, game_id)
    try:
        try:
            async for message in websocket:
                print(f"{game_id}#{user_id}: {message}")
                await notify(message, game_id)
        except websockets.ConnectionClosedError:
            pass
    finally:
        await unregister(websocket, game_id)

if __name__ == '__main__':
    IP, PORT = "0.0.0.0", int(os.environ.get('SIMON_PORT', "3316"))
    start_server = websockets.serve(relay, IP, PORT)

    print(f"Listening on {IP}:{PORT}")

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
