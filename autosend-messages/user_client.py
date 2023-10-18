import json
from os import path, getcwd
from datetime import datetime, timedelta

import asyncio
from pyrogram import Client
import mysql.connector.errors

from utilities.DBcm import *
from utilities.config import config_setter

# if config haven't been set yet
if not path.exists(path.join(getcwd(), 'config.json')):
    config_setter()

with open('utilities/config.json', mode='r') as r_file:
    config = json.load(r_file)

client = Client(config.get('session'),
                config.get('api_id'),
                config.get('api_hash'))

# adjust to your preferences
time_until_sending = timedelta(hours=2)

""" 
    following code is a prototype: 
    it's main task is to show the async algorithm
    ---------------------------------------------
    by Flowzy
"""

async def event_listener(queue: asyncio.Queue):
    try:
        while True:
            async with client:
                user_data = await client.get_me()
                last_time_seen = user_data.last_online_date
                if last_time_seen is not None:
                    await queue.put(last_time_seen)

            await asyncio.sleep(3)

    except asyncio.CancelledError:
        print("Program has finished")


async def timer(queue: asyncio.Queue):
    while True:
        last_time_seen = await queue.get()
        current_time = datetime.now()
        time_diff = current_time - last_time_seen

        print(f"Current time  : {current_time}",
              f"Last time seen: {last_time_seen}", sep="\n")

        if time_diff > time_until_sending:
            try:
                with UseDatabase(dbconfig) as cursor:
                    _SQL = """select * from user_message"""
                    cursor.execute(_SQL)
                    for message, user in cursor.fetchall():
                        print(message, user)

                        # put code to message sending here

                    print("Messages has been sent")
                    return

            except mysql.connector.errors.Error as ex:
                print(ex.msg,
                      ex.errno,
                      ex.sqlstate, sep='\n')
        else:
            await asyncio.sleep(3)


async def main():
    queue = asyncio.Queue(1)
    event_listener_task = asyncio.create_task(event_listener(queue))
    timer_task = asyncio.create_task(timer(queue))

    await timer_task
    if timer_task.done():
        event_listener_task.cancel()
    await event_listener_task


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass
    except Exception as error:
        print(error,
              error.args, sep="\n")
