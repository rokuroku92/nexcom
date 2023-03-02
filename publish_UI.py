# -*- coding:utf-8 -*-
import paho.mqtt.client as mqtt
import mysql.connector
import Config
from util import Conn


# 發佈
def publish(data, timestamp):
    # 建立資料庫連線
    mydb_pool = Conn.get_mydb_pool()
    mydb = mydb_pool.get_connection()
    mycursor = mydb.cursor(buffered=True)

    address = Config.address
    port = Config.port
    topic = Config.topic_pub

    client = mqtt.Client()
    # print("data: "+data)
    # print("timestamp: "+timestamp)
    client.on_connect = lambda client, userdata, flags, rc: {
        print("Connected with result code(發佈): " + str(rc))
    }
    '''
    client.on_message = lambda client, userdata, msg: {
        print(msg.topic + " " + str(msg.payload))
    }
    '''
    client.connect(address, port, 60)
    client.will_set(topic=Config.topic_pub, qos=1)
    client.loop_start()
    # 發送字串

    station = int((int(data) - 1) / 10)
    cmd = int(data) % 10
    status = ''
    # print("------")
    if ((int(cmd) == 1) | (int(cmd) == 5)) & (int(station) != 7):
        # 先查詢DB資料各站點最後一列資料是否重複
        sql = "select a.station_id,a.cmd_id,a.timestamp_id from YID.c2a a where " \
              "a.c2a_id in (SELECT max(a.c2a_id) FROM YID.c2a a group by a.station_id)ORDER BY a.station_id ASC "
        mycursor.execute(sql)
        result = mycursor.fetchall()
        # print("+++++++++++")
        # 時間或命令不相同時則記入DB
        if (str(result[station-1][2]) != str(timestamp)) | (str(result[station-1][1]) != str(cmd)):
            # 新增 c2a
            sql = "INSERT INTO c2a (timestamp_id, station_id, ack_handshaking, cmd_id) VALUES (%s, %s, %s, %s)"
            val = (timestamp, station, "", cmd)
            mycursor.execute(sql, val)
            mydb.commit()

        # 新增 log

        mycursor = mydb.cursor()
        sql = "INSERT INTO log (timestamp_id, station_id, ack_handshaking, cmd_id) VALUES (%s, %s, %s, %s)"
        val = (timestamp, station, "", cmd)
        mycursor.execute(sql, val)
        mydb.commit()
    elif int(station) == 7:
        # 先查詢DB資料倉庫的最後一列資料是否重複
        sql = "SELECT cmd_id,timestamp_id FROM warehouse_error ORDER BY warehouse_error_id DESC LIMIT 1"
        mycursor.execute(sql)
        result = mycursor.fetchone()
        if (str(result[1]) != str(timestamp)) | (str(result[0]) != str(cmd)):
            # 新增 warehouse_error
            sql = "INSERT INTO warehouse_error (timestamp_id, station_id, ack_handshaking, cmd_id) VALUES (%s, %s, %s, %s)"
            val = (timestamp, station, "", cmd)
            mycursor.execute(sql, val)
            mydb.commit()

        # 新增 log
        mycursor = mydb.cursor()
        sql = "INSERT INTO log (timestamp_id, station_id, ack_handshaking, cmd_id) VALUES (%s, %s, %s, %s)"
        val = (timestamp, station, "", cmd)
        mycursor.execute(sql, val)
        mydb.commit()

    station = int(station)
    if int(cmd) == 1:
        cmd = 'transfer'
    elif int(cmd) == 5:
        cmd = 'error-fixed'
    if int(station) == 7:
        station = "warehouse"

    msg = '{"cmd": "' + str(cmd) + '", "transfer_id": "' + timestamp + '", "station": "' + str(
                    station) + '", "status": "' + status + '"}'
    client.publish(topic, payload=msg, qos=0)
    mydb.close()
    mycursor.close()
