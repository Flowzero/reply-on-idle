
import mysql.connector

# provide your database data below

dbconfig = {'host': '',
            'user': '',
            'password': '',
            'database': ''}


class UseDatabase:

    def __init__(self, configuration):
        self.config = configuration

    def __enter__(self):
        self.conn   = mysql.connector.connect(**self.config)
        self.cursor = self.conn.cursor(buffered=True)
        # using buffered to avoid InternalError as it generates
        # when not all data was pulled out from the database
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.cursor()
