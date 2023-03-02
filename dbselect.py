# -*- coding:utf-8 -*-
import time
import mysql.connector
import mqtt.publish_UI as mq

while True:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="yid"
    )
    mqt_pub = mq.PublishUI()
    mycursor = mydb.cursor()

    # sql = "select a.station_id,a.cmd_id,a.ack_handshaking,a.timestamp_id from " \
    #       "YID.c2a a where a.c2a_id in (SELECT max(a.c2a_id) FROM YID.c2a a group by a.station_id)"
    # mycursor.execute(sql)
    # result = mycursor.fetchall()
    # # print(result)
    # for i in range(1, 7):
    #     # print("ack_handshaking: "+result[i][2])
    #     if result[i][2] != 'A':
    #         # mqt_pub.publish(str(str(result[i][0]) + str(result[i][1])), result[i][3])
    #         print(str(str(result[i][0]) + str(result[i][1])) + ", " + result[i][3])
    # mydb.commit()
    #
    # mycursor = mydb.cursor()
    # sql = "SELECT w.station_id,w.ack_handshaking,w.cmd_id,w.timestamp_id FROM YID.warehouse_error w where w.warehouse_error_id " \
    #       "in (SELECT max(w.warehouse_error_id) FROM YID.warehouse_error w where w.cmd_id=5);"
    # mycursor.execute(sql)
    # result = mycursor.fetchone()
    # # print(result)
    # if result[1] != 'A':
    #     # mqt_pub.publish("75", result[3])
    #     print("75, " + result[3])
    # mydb.commit()
    # print("check")
    time.sleep(1)

    sql = "select a.station_id,a.cmd_id,a.timestamp_id from YID.c2a a where " \
          "a.c2a_id in (SELECT max(a.c2a_id) FROM YID.c2a a group by a.station_id)ORDER BY a.station_id ASC "
    mycursor.execute(sql)
    result = mycursor.fetchall()
    # mycursor.execute(sql)
    # result = mycursor.fetchone()
    print(result)
    print(result[1][2])
    # if (str(result[1]) != str(timestamp)) & (str(result[0]) != str(cmd)):