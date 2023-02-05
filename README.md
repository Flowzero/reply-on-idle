 
Automatic message sending based on the user's activity on Telegram. 
Program allows you to pre-write messages which will be sent to users you choose if you won't appear online for some time.

## MAIN PART ##

Here’s a quick explanation which will navigate you through the project:
 1. Log in on  [my.telegram.org](https://my.telegram.org/auth?to=apps) to get development data. We’ll need it later.
 
 2. [Create a database](https://dev.mysql.com/doc/refman/8.0/en/create-database.html) (or use local files instead. If you do so, consider that you’ll have to rewrite save data functions in all parts of the program)
 
 ```sql
 create database user_activity;
 ```
 
  3. You have to create following tables in database:

```sql
create table user_data (
	id bigint not null,
    	user varchar(64) not null,
    	timezone char(32) not null,
    	last_seen timestamp not null
    	);
    
```

```sql
create table user_message(
	message_self varchar(4096) not null,
    	users_nicks varchar(1024) not null
    	);
```
4. Open get_me_client/utilts/DBcm.py and put your database configuration into dbconfig.

5. Download all necessary packages (from requirements.txt)



## OPTIONAL PART ##

If you want to use bot for saving messages and users to the database, consider following steps:

1. Create additional table in your database:

```sql
create table user_config (
	operation_id bigint not null,
	user_lang varchar(32) not null,
    	user_timezone varchar(128) not null
    	);
```
2. (Optional) Open info_bot/bot_utilts/DBcm.py and put your database configuration into dbconfig (you can ignore this part if you don’t need to use the bot)

3. (Optional) Get bot token from [BotFather](https://stackoverflow.com/questions/48109170/where-can-i-find-the-telegram-bot-api-token) (if you want to use bot) after this open info_bot/client_bot.py and put it into bot token valuable

```python
# put your bot token  below
bot_token = ''
```


## RUN GUIDE ##

Here’s specific order you have to follow:

1. Save messages and users you want to send the messages to the database before running any scripts. It needs to be done to guarantee the program won't crash trying to get data which does not exist. (You can save data manually or by using telegram bot - optional part)

2. Save messages and users you want to send the messages to the database before running any scripts. It needs to be done to guarantee the program won't crash trying to get data which does not exist. (You can save data manually or by using telegram bot - optional part)

3. Run User client reply 
