# -*- coding:utf-8 -*-
import mysql.connector

from datetime import datetime

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="YID"
)

mycursor = mydb.cursor()

mycursor.execute("SHOW TABLES")

for x in mycursor:
    print(x)

# 新增 warehouse_error 資料列

mycursor = mydb.cursor()

# 新增 warehouse_error
sql = "INSERT INTO warehouse_error (timestamp_id, station_id, ack_handshaking, cmd_id) VALUES (%s, %s, %s, %s)"
val = ("", "1", "C", "2")
mycursor.execute(sql, val)
mydb.commit()
warehouse_error_id = mycursor.lastrowid
print(warehouse_error_id, " record inserted.")

# 取得 timestamp_id
timestamp_id = (datetime.now().strftime('%Y%m%d%H%M%S%f'))

# 回寫 timestamp_id
sql = "update warehouse_error set timestamp_id = '" + str(timestamp_id) + "' where warehouse_error_id = " + str(warehouse_error_id);
print(sql)
mycursor.execute(sql)
mydb.commit()

print('回寫 timestamp_id OK')
