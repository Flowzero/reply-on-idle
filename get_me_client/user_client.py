# This code meets python 3.11 conditions

import logging

from telethon.sync import TelegramClient, events
from telethon.tl.types import UserStatusOffline
import mysql.connector.errors
import datetime
import logging
import json
import os

from utilts.config import config_setter
from utilts.DBcm import UseDatabase
from utilts.DBcm import dbconfig

# fill dbconfig in utils.DBcm with your data

# recommended to enable logging when working with events
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

# if config haven't been set yet
if not os.path.exists(os.path.join(os.getcwd(), 'config.json')):
    config_setter()

with open('config.json', mode='r') as r_file:
    config = json.load(r_file)

client = TelegramClient(config.get('session'),
                        config.get('api_id'),
                        config.get('api_hash'))

# ___________________filter function___________________

def db_empty(*args, **kwargs):
    with UseDatabase(dbconfig) as cursor:
        _SQL = """select count(*) from user_data"""
        cursor.execute(_SQL)
        if cursor.fetchall()[-1][0] == 0:
            return True
        else:
            return False

# ___________________MAIN PART WITH ASYNCIO ___________________

@client.on(events.UserUpdate(func=db_empty))
async def handler(event: events.UserUpdate.Event):
    user_data = await client.get_entity(
        await client.get_me()
    )
    print(user_data.__dict__.get('status'))

    if isinstance(user_data.status, UserStatusOffline):
        last_seen = user_data.status.was_online # utc+0
        print('Last time seen at', last_seen)
        with UseDatabase(dbconfig) as cursor:
            try:
                _SQL = """insert into user_data
                          (id, user, timezone, last_seen)
                          values
                          (%s, %s, %s, %s)"""
                cursor.execute(_SQL, (user_data.id,
                                      user_data.first_name,
                                      'Europe/London - UTC +00:00',
                                      last_seen))

            except mysql.connector.errors.DatabaseError as DB_Error:
                print("Error Code:", DB_Error.errno)
                print("SQLSTATE", DB_Error.sqlstate)
                print("Message:", DB_Error.msg)


@client.on(events.UserUpdate(func=not db_empty))
async def process_handler(event: events.UserUpdate.Event):
    user_data = await client.get_entity(
        await client.get_me()
    )
    print(user_data.__dict__.get('status'))
    if isinstance(user_data.status, UserStatusOffline):
        last_seen: datetime = user_data.status.was_online
        print('Last time seen at', last_seen)
        with UseDatabase(dbconfig) as cursor:
            try:
                _SQL = """update user_data
                          set last_seen = %s
                          where
                          id = %s"""
                cursor.execute(_SQL, (last_seen,
                                      user_data.id))
            except mysql.connector.errors.DatabaseError as DB_Error:
                print("Error Code:", DB_Error.errno)
                print("SQLSTATE", DB_Error.sqlstate)
                print("Message:", DB_Error.msg)


if __name__ == '__main__':
    try:
        client.start()
        client.run_until_disconnected()
    except KeyboardInterrupt:
        pass
