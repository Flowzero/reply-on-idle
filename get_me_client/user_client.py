import os
import json
import datetime

import asyncio
from pyrogram import Client

from utilities.DBcm import *
from utilities.config import config_setter

# if config haven't been set yet
if not os.path.exists(os.path.join(os.getcwd(), 'config.json')):
    config_setter()

with open('config.json', mode='r') as r_file:
    config = json.load(r_file)

client = Client(config.get('session'),
                config.get('api_id'),
                config.get('api_hash'))


async def event_listener(queue: asyncio.Queue):
    while queue.qsize() != 2:
        async with client:
            user_data = await client.get_me()
            user_last_seen = user_data.last_online_date
            if user_last_seen != None:
                await queue.put(user_last_seen)

            # data must be not None

        await asyncio.sleep(10)


async def timer_send(queue: asyncio.Queue):
    while True:
        user_last_seen = await queue.get()
        current_time = datetime.datetime.now()
        time_diff = current_time - user_last_seen
        print(f'Current time: {current_time}\n Last seen: {user_last_seen}')
        if time_diff > datetime.timedelta(minutes=5):
            with UseDatabase(dbconfig) as cursor:
                _SQL = """select * from user_message"""
                cursor.execute(_SQL)
                for message, user in cursor.fetchall():
                    print(message, user)

                    # put your code for message sending here

            print('Messages sent')
            queue.put_nowait('Stop event_listener')
            break
        else:
            await asyncio.sleep(10)

    print('The program will shut down soon...')


async def main():
    queue = asyncio.Queue(2)
    event_listener_task = asyncio.create_task(event_listener(queue))
    timer_send_task = asyncio.create_task(timer_send(queue))
    await asyncio.gather(timer_send_task, event_listener_task)


try:
    asyncio.get_event_loop().run_until_complete(main())  # both task must be finished
except KeyboardInterrupt:
    pass
except RuntimeError:
    pass
