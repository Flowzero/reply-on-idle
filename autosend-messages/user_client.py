import os
import sys
import json
import datetime

import asyncio
from pyrogram import Client
import mysql.connector.errors

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
    while True: # sys.exit() when reaching executive code
                # no need to break the cycle
        async with client:
            user_data = await client.get_me()
            user_last_seen = user_data.last_online_date
            if user_last_seen is not None:
                await queue.put(user_last_seen)

        await asyncio.sleep(10)


async def timer_send(queue: asyncio.Queue):
    while True:
        user_last_seen = await queue.get()
        current_time = datetime.datetime.now()
        time_diff = current_time - user_last_seen
        print(f'Current time: {current_time}')
        print(f'Last seen   : {user_last_seen}')
        if time_diff > datetime.timedelta(hours=2):
            try:
                with UseDatabase(dbconfig) as cursor:
                    _SQL = """select * from user_message"""
                    cursor.execute(_SQL)
                    for message, user in cursor.fetchall():
                        print(message, user)

                        # put your code for message sending here

                print('Messages sent')
                sys.exit()
            except mysql.connector.errors.Error as ex:
                print(ex.msg)
                print(ex.errno)
                print(ex.sqlstate)
        else:
            await asyncio.sleep(10)


async def main():
    queue = asyncio.Queue(1)
    event_listener_task = asyncio.create_task(event_listener(queue))
    timer_send_task = asyncio.create_task(timer_send(queue))
    await asyncio.gather(timer_send_task, event_listener_task)


try:
    asyncio.get_event_loop().run_until_complete(main())  # both task must be finished
except KeyboardInterrupt:
    pass
except RuntimeError:
    pass
