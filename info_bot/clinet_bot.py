# This code meets python 3.11 conditions

import logging

import mysql.connector.errors
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
from mysql.connector.errors import DatabaseError
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
import pytz
import re

from bot_utilts.time_convert import timezones
from bot_utilts.DBcm import UseDatabase, dbconfig

# provide your data into dbconfig

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

# put your bot token below
bot_token = ''

bot = Bot(token=bot_token, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# put your friends ids in the list
friends_ids = []

localFormatEu = "%H:%M:%S %Y-%d-%m"
localFormatUs = "%H:%M:%S %Y-%m-%d"


# _____________________FSM CONTEXT CLASSES_____________________


class Requirements(StatesGroup):
    users = State()
    message = State()
    confirm = State()


class Config(StatesGroup):
    language = State()
    user_timezone = State()


# _____________________UTILTS FUNCTIONS_____________________


def get_ip_from_db():
    with UseDatabase(dbconfig) as cursor:
        _SQL = """select id from user_data"""
        cursor.execute(_SQL)
        user_id = cursor.fetchall()[-1][0]
    return user_id


def user_lang(user_id):
    with UseDatabase(dbconfig) as cursor:
        _SQL = """select user_lang
                  from user_config
                  where operation_id = %s"""
        cursor.execute(_SQL, (user_id,))
        user_lang = cursor.fetchone()[0]
        print(user_lang)
    return user_lang


@dp.message_handler(commands=['cancel'], state='*')
async def command_cancel_handler(message: types.Message, state: FSMContext):
    # Allow user to cancel any action
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelled state %r', current_state)
    await state.finish()
    # Removing keyboard just in case
    await message.reply("Cancelled", reply_markup=types.ReplyKeyboardRemove())


# ____________________________________________________START_____________________________________________________________


def lang_keyboard():
    buttons = [
        types.InlineKeyboardButton(text='English 🇺🇸', callback_data='select_en'),
        types.InlineKeyboardButton(text='Русский 🇷🇺', callback_data='select_ru'),
    ]
    # row_width = 2: makes button on the same row
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


@dp.message_handler(commands=['start'])
async def log_handler(message: types.Message):
    user_ids_db = []
    user_id = message.from_user.id
    with UseDatabase(dbconfig) as config_cursor:
        _SQL = """select operation_id from user_config"""
        config_cursor.execute(_SQL)
        response = config_cursor.fetchall()
        for item in response:
            for elem in item:
                user_ids_db.append(elem)

        if len(response) == 0 or user_id not in user_ids_db:
            await Config.language.set()
            await message.answer("Select the language\n\nВыберите язык",
                                 reply_markup=lang_keyboard())
        else:
            lang = user_lang(user_id)
            if lang == 'ru':
                await message.answer("Вы уже создали конфигурацию")
            if lang == 'en':
                await message.answer("You already have config")


@dp.callback_query_handler(text='select_en', state=Config.language)
async def callback_query_select_en_handler(call: types.CallbackQuery, state: FSMContext):
    global lang
    lang = 'en'
    await state.update_data(language='en')
    await call.message.edit_reply_markup()
    await call.message.answer(
        "Provide your timezone. It should be given in following format:\n" +
        "<code>Europe/Berlin</code> (first param is continent, the second one" +
        "is big city which located in that timezoone)"
    )
    await call.message.delete()
    await Config.next()


@dp.callback_query_handler(text='select_ru', state=Config.language)
async def callback_query_select_en_handler(call: types.CallbackQuery, state: FSMContext):
    global lang
    lang = 'ru'
    await state.update_data(language='ru')
    await call.message.edit_reply_markup()
    await call.message.answer(
        "Укажите вашу временную зону. Она должна быть в следующем формате:\n" +
        "<code>Europe/Berlin</code> (первый параметр - континет, второй -" +
        "большой город, находящийся в этом часовом поясе)"
    )
    await call.message.delete()
    await Config.next()


@dp.message_handler(state=Config.language)
async def config_lang_handler(message: types.Message, state: FSMContext):
    global lang
    await state.update_data(language=lang)
    if lang == 'en':
        await message.answer(
            "Provide your timezone. It should be given in following format:\n" +
            "<code>Europe/Berlin</code> (first param is continent, the second one" +
            "is big city which located in that timezoone)"
        )
    if lang == 'ru':
        await message.answer(
            "Укажите вашу временную зону. Она должна быть в следующем формате:\n" +
            "<code>Europe/Berlin</code> (первый параметр - континет, второй -" +
            "большой город, находящийся в этом часовом поясе)"
        )
    await Config.next()


@dp.message_handler(state=Config.user_timezone)
async def user_timzone_handler(message: types.Message, state: FSMContext):
    global user_tz
    user_tz = message.text
    user_id = message.from_user.id
    await state.update_data(user_timezone=message.text)
    await state.finish()
    with UseDatabase(dbconfig) as cursor_conf:
        _SQL = """insert into user_config
                  (operation_id, user_lang, user_timezone)
                  values
                  (%s, %s, %s)"""
        cursor_conf.execute(_SQL, (user_id, lang, user_tz))


# _________________________________________________SETTINGS_____________________________________________________________
@dp.message_handler(commands=['settings'])
async def setting_handler(message: types.Message):
    args = message.get_args().split()
    user_id = message.from_user.id
    if len(args) == 2:
        global lang, user_tz
        lang, user_tz = args[0], args[1]

        with UseDatabase(dbconfig) as insert_cursor:
            _SQL = f"""update user_config 
                      set 
                      user_lang = '%s', 
                      user_timezone = '%s' 
                      where operation_id = '%s';""" % (lang, user_tz, user_id)
            insert_cursor.execute(_SQL)

        if lang == 'ru':
            await message.answer(
                "Настройки бота были обнавлены:\n\nВыбранный вами язык: <b>Русский</b>\n" +
                f"Временая зона, в которой будут отображаться сообщения: <b>{args[1]}</b>\n\n" +
                "Вы можете менять временную зону прямо в команде <code>/info</code>\n" +
                "Для этого укажие допалнительный аргумент - временную зону. " +
                "Пример команды:\n <code>/info Europe/Berlin</code>"
            )
        if lang == 'en':
            await message.answer(
                "Settings has been updated:\n\nSelected language: <b>English</b>\n" +
                f"The time zone in which the messages will be displayed: <b>{args[1]}</b>\n\n" +
                "You can change the time zone directly in the command <code>/info</code>\n" +
                "To do this, specify an additional argument - the time zone. " +
                "Command example:\n <code>/info Europe/Berlin</code>"
            )


# __________________________________________________REGISTER____________________________________________________________

@dp.message_handler(commands=['register'])
async def command_register_handler(message: types.Message):
    user_id = get_ip_from_db()
    lang = user_lang(message.from_user.id)
    if user_id == message.from_user.id:
        await Requirements.users.set()
        if lang == 'ru':
            await message.answer("Пожалуйста, предоставьте пользователей, которым хотите отправить сообщения." +
                                 "(Имена пользователей должны быть разделены пробелом и без символа @)")
        if lang == 'en':
            await message.answer("Please, provide users you want to send messages " +
                                 "(User names must be separated by a space and without a character @)")
    else:
        if lang == 'ru':
            await message.answer("У вас нет прав для использования этой комманды")
        if lang == 'en':
            await message.answer("You have no rights to use this command")


@dp.message_handler(lambda message: re.fullmatch(r'(\w+\s)+\w+|\w+', message.text), state=Requirements.users)
async def process_users_id(message: types.Message, state: FSMContext):
    global users_ids
    users_ids = message.text

    await state.update_data(users=message.text)
    print(users_ids)
    lang = user_lang(message.from_user.id)
    if lang == 'ru':
        await message.answer("Пожалуйста, напишите сообщение, которое вы хотите отправить пользователям. " +
                             "(Это сообщение будет отправлено всем пользователям, которых вы указали выше)")
    if lang == 'en':
        await message.answer("Please, write message you want to send to the users you have provided. " +
                             "(This message will be sent to all users provided above)")
    await Requirements.next()


@dp.message_handler(lambda message: not re.fullmatch(r'(\w+\s?)+\w+|(\w+)', message.text), state=Requirements.users)
async def invalid_format_users(message: types.Message):
    lang = user_lang(message.from_user.id)
    if lang == 'ru':
        await message.answer("Пожалуйста, будьте осторожны, когда пишете ники: " +
                             "вы не разделили их пробелом или написали их с @")
    if lang == 'en':
        await message.answer("Please, be careful when providing usernames: you didn't  " +
                             "provide it separated by spaces or you put @ into usernames")


def get_keyboard_en():
    # keyboard generation
    buttons = [
        types.InlineKeyboardButton(text='Confirm ✅', callback_data='confirmation'),
        types.InlineKeyboardButton(text='Cancel ❌', callback_data='cancellation'),
    ]
    # row_width = 2: makes button on the same row
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def get_keyboard_ru():
    buttons = [
        types.InlineKeyboardButton(text='Подтвердить ✅', callback_data='confirmation'),
        types.InlineKeyboardButton(text='Отменить ❌', callback_data='cancellation'),
    ]
    # row_width = 2: makes button on the same row
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


@dp.message_handler(state=Requirements.message)
async def process_message(message: types.Message, state: FSMContext):
    global user_message
    user_message = message.text
    await state.update_data(message=message.text)
    await state.finish()
    print(users_ids, user_message)
    lang = user_lang(message.from_user.id)
    if lang == 'ru':
        await message.answer("Вы уверены, что хотите отправить сообщение указанным пользоваелям?\n" +
                             f"{', '.join(users_ids.split())}",
                             reply_markup=get_keyboard_ru())
    if lang == 'en':
        await message.answer("Are you sure you want to send the message to following users?\n" +
                             f"{', '.join(users_ids.split())}",
                             reply_markup=get_keyboard_en())


@dp.callback_query_handler(text='confirmation')
async def callback_query_confirmation_handler(call: types.CallbackQuery):
    await call.message.answer('Yes, confirmed')
    await call.message.edit_reply_markup()
    with UseDatabase(dbconfig) as cursor_transfer:
        try:
            _SQL = '''insert into user_message
                      (message_self, users_nicks)
                      values
                      (%s, %s)'''
            cursor_transfer.execute(_SQL, (user_message,
                                           users_ids))
        except mysql.connector.errors.DatabaseError as DB_Error:
            print("Error Code:", DB_Error.errno)
            print("SQLSTATE", DB_Error.sqlstate)
            print("Message:", DB_Error.msg)


@dp.callback_query_handler()
async def callback_query_cancellation_handler(call: types.CallbackQuery):
    lang = user_lang(call.from_user.id)
    if lang == 'ru':
        await call.message.answer("Отменено")
        await call.message.edit_reply_markup()
    if lang == 'en':
        await call.message.answer('Cancelled')
        await call.message.edit_reply_markup()


# ______________________________________________________INFO____________________________________________________________

@dp.message_handler(regexp=re.compile(r'/info (.+)|(/info)'))
async def command_info_handler(message: types.Message, regexp: re.Match):
    lang = user_lang(message.from_user.id)
    user_id = message.from_user.id
    to_timezone = regexp[1]
    # message.get_args().split()

    if user_id in friends_ids:
        try:
            # last_seen db request
            with UseDatabase(dbconfig) as cursor:
                _SQL = """select last_seen
                          from user_data"""
                cursor.execute(_SQL)
                user_last_seen = cursor.fetchall()[-1][0]
                print(user_last_seen)

            # user_tz db request
            with UseDatabase(dbconfig) as cursor:
                _SQL = """select user_timezone from user_config where operation_id = %s"""
                cursor.execute(_SQL, (user_id,))
                user_tz = cursor.fetchall()[-1][0]
                print(user_tz)

            if to_timezone is None:
                # use users timezone
                await message.answer(user_last_seen.astimezone(tz=pytz.timezone(user_tz))\
                                     .strftime(localFormatEu))

            if to_timezone in timezones:
                await message.answer(user_last_seen.astimezone(tz=pytz.timezone(to_timezone))\
                                     .strftime(localFormatEu))

        except DatabaseError as DB_Error:
            print("Error Code:", DB_Error)
        except SyntaxError as err:
            print(err)

    # main handler added


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
