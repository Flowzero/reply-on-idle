 
Automatic message sending based on the user's online status on Telegram. 
Program allows you to pre-write messages which will be sent to users you specify if you won't appear online until the timer runs out. Every time you appear online the timer resets.


## General principle of operation ##
A queue is created in the main function, through which the coroutines will be 
exchanged with data. Next, tasks are created and gathered together. 

Event_listener is a simple example of exactly what its name says. The function tracks the time of the last activity in 
Telegram and passes this value to the timer function. Don't worry about the infinite loop - it will break when the timer 
runs out. 

The timer_send function is a timer that gets the time of the last activity and makes the following comparison: if more 
time has passed since the last activity than specified, the message sending function is triggered.

```python
if time_diff > datetime.timedelta(hours=2):
    with UseDatabase(dbconfig) as cursor:
        _SQL = """select * from user_message"""
        cursor.execute(_SQL)
               ...

            
```

## Important note ##
Before you start working with the program, do not forget to specify the connection data to your database (in the 
file DBcm.py ). If you don't know how to create a database and what you need for this, visit the [official MySQL 
website](https://dev.mysql.com/doc/refman/8.0/en/creating-database.html)

```python
dbconfig = {'host': '', 
            'user': '',
            'password': '',
            'database': ''}
```
In a new SQL document, write this code and execute it (You can copy and paste it. Do not forget to put your database 
name) - this will create a database table 
where you can enter recipients and messages.
```sql
use <name of your database>;

create table user_message(
    message_self varchar(4096) not null,
    users_nicks varchar(1024) not null
    );
```
You can add data to your database, follow this [guide](https://dev.mysql.com/doc/refman/8.0/en/insert.html)
