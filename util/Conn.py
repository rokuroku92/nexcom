import mysql.connector
import Config
from mysql.connector import pooling

mydb_pool = None

def get_mydb_pool():
    global mydb_pool
    if mydb_pool == None:
        mydb_config = {
            "host": Config.host,
            "user": Config.user,
            "password": Config.password,
            "database": Config.database,
            "buffered": True
        }
        mydb_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="yid",
                                       pool_size=32,  # 0~32 最大只能是 32
                                    **mydb_config)
    return mydb_pool
