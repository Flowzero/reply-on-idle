# This code meets python 3.11 conditions

import datetime
import asyncio
import json

import mysql.connector.errors
from telethon import TelegramClient

from utilts.DBcm import UseDatabase
from utilts.DBcm import dbconfig


# config reader
with open('config.json', mode='r') as r_file:
    config = json.load(r_file)


async def main():
    trigger = True

    while trigger:
        with UseDatabase(dbconfig) as cursor:
            _SQL = """select last_seen from user_data"""
            cursor.execute(_SQL)
            user_last_seen = cursor.fetchall()[-1][0]
            current_time   = datetime.datetime.utcnow()
            print("Last seen: ", user_last_seen,
                  "Current time: ", current_time, sep='\n')

        # default timeout is 2 minutes. You can adjust it manually

        time_temp = datetime.datetime(2023, 1, 1, 13, 10)
        time_temp_ = datetime.datetime(2023, 1, 1, 13, 8)

        if current_time - user_last_seen > time_temp - time_temp_:
            # class TelegramClient does not define __await__, it's okay
            client = await TelegramClient(config.get('session'),
                                          config.get('api_id'),
                                          config.get('api_hash')).start()
            try:
                with UseDatabase(dbconfig) as cursor:
                    _SQL = """select * from user_message"""
                    cursor.execute(_SQL)
                    for message, users in cursor.fetchall():
                        print(message, users)
                        await asyncio.wait([
                            asyncio.create_task(client.send_message(user, message))
                            for user in users.split()
                        ])

                await client.disconnect()
                trigger = False
            except mysql.connector.errors.OperationalError:
                await asyncio.sleep(10)

        await asyncio.sleep(60)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
