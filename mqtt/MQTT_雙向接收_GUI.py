import threading
import time
import paho.mqtt.client as mqtt
import json
import mysql.connector
# import multi_tk_app as a

class Mqtt_GUI():

    # 建立資料庫連線
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="yid"
    )
    mycursor = mydb.cursor()

    address = "192.168.1.210"
    port = 1883
    topic = "/missionA2C"



    def __init__(self):
        # root.title('MQTT')
        # root.geometry("300x200")
        # text = tk.StringVar()
        # text.set("1")
        # self.entry = tk.Entry(root, textvariable=text)
        # self.entry.pack()
        # self.button = tk.Button(root)
        # self.button.config(text="Pub", command=self.publish)
        # self.button.pack()
        pass


    def startthread(self):
        # 啟動訂閱服務執行緒
        newthread = threading.Thread(target=self.sub)
        newthread.start()

    def json_pack(self):
        pass

    # 訂閱內容處理
    def handle_msg(self, msg):
        mystr = str(msg.payload.decode())
        print("訂閱接收: " + msg.topic + " " + mystr)
        # 分析 json 字串
        dict = json.loads(mystr)  # 將 str 轉 dict 格式
        cmd = dict['cmd'].strip()  # 去除左右空白 .strip()
        station = dict['station'].strip()
        timestamp = dict['transfer_id'].strip()
        status = dict['status'].strip()
        print('訂閱接收(分析 json 字串):', timestamp, type(timestamp), cmd, type(cmd), station, type(station))

        if cmd == 'transfer':
            cmd = 1
        if cmd == 'roll-out':
            cmd = 2
        if cmd == 'completed':
            cmd = 3
        if cmd == 'error':
            cmd = 4
        if cmd == 'error-fixed':
            cmd = 5

        if (int(cmd) == 2) | (int(cmd) == 3) | (int(cmd) == 4):
            sql = "SELECT timestamp_id FROM a2c ORDER BY a2c_id DESC LIMIT 1"
            self.mycursor.execute(sql)
            result = self.mycursor.fetchone()
            if str(result) != str("('" + timestamp + "',)"):
                # 新增 a2c
                sql = "INSERT INTO a2c (timestamp_id, station_id, ack_handshaking, cmd_id) VALUES (%s, %s, %s, %s)"
                val = (timestamp, station, "", cmd)
                self.mycursor.execute(sql, val)
                self.mydb.commit()
                # if cmd == 2:
                #     x = station + "41"
                #     a.App.send(sc, x)
                # if cmd == 3:
                #     x = station + "30"
                #     a.App.send(sc, x)
                # if cmd == 4:
                #     x = station + "51"
                #     a.App.send(sc, x)
            self.publish(str(str(station) + str(cmd)), timestamp)
            # 新增 log
            sql = "INSERT INTO log (timestamp_id, station_id, ack_handshaking, cmd_id) VALUES (%s, %s, %s, %s)"
            val = (timestamp, station, status, cmd)
            self.mycursor.execute(sql, val)
            self.mydb.commit()

        elif (int(cmd) == 1) | (int(cmd) == 5):
            if status == 'OK':
                sql = "SELECT c2a_id FROM c2a ORDER BY c2a_id DESC LIMIT 1"
                self.mycursor.execute(sql)
                c2a_id = self.mycursor.fetchone()
                c2a_id = str(c2a_id).strip("'").strip("(").strip(")").replace(",", "")
                print(c2a_id, type(c2a_id))
                # 回寫 ack_handshaking
                sql = "update c2a set ack_handshaking = 'A' where c2a_id = " + str(c2a_id)
                print(sql)
                self.mycursor.execute(sql)
                self.mydb.commit()

                # if cmd == 1:
                #     x = station + "31"
                #     a.App.send(sc, x)
            else:
                self.publish(str(station + cmd), timestamp)
                time.sleep(1)

            self.mycursor = self.mydb.cursor()
            # 回寫 log ack_handshaking
            sql = "SELECT log_id FROM log ORDER BY log_id DESC LIMIT 1"
            self.mycursor.execute(sql)
            log_id = self.mycursor.fetchone()
            log_id = str(log_id).strip("'").strip("(").strip(")").replace(",", "")
            print(log_id, type(log_id))
            # 回寫 ack_handshaking
            sql = "update log set ack_handshaking = 'A' where log_id = " + str(log_id)
            print(sql)
            self.mycursor.execute(sql)
            self.mydb.commit()

        else:
            print("Command error")

    # 訂閱
    def sub(self):
        client = mqtt.Client()
        client.on_connect = lambda client, userdata, flags, rc: {
            print("Connected with result code(訂閱): " + str(rc))
        }
        client.on_message = lambda client, userdata, msg: {
            # 接收字串
            self.handle_msg(msg)
        }
        client.connect(self.address, self.port, 60)
        client.subscribe(self.topic)
        # 持續接收
        client.loop_forever()


    # 發佈
    def publish(self, data, timestamp):
        address = "192.168.1.210"
        port = 1883
        topic = "/missionC2A"
        client = mqtt.Client()

        client.on_connect = lambda client, userdata, flags, rc: {
            print("Connected with result code(發佈): " + str(rc))
        }
        '''
        client.on_message = lambda client, userdata, msg: {
            print(msg.topic + " " + str(msg.payload))
        }
        '''
        client.connect(address, port, 60)
        client.loop_start()
        # 發送字串

        station = int(data) / 10
        cmd = int(data) % 10
        status = ''

        if (str(int(cmd)) == '2') | (str(int(cmd)) == 3) | (str(int(cmd)) == 4):
            status = 'OK'

        msg = '{"cmd": "' + str(int(cmd)) + '", "transfer_id": "' + timestamp + '", "station": "' + str(int(station)) + '", "status": "' + status + '"}'
        client.publish(topic, payload=msg, qos=0)



if __name__ == '__main__':
    #root = tk.Tk()
    # sc = a.App(root)
    app = Mqtt_GUI()
    #root.after(1000, app.startthread())
    # root.after(100, app.publish('11'))
    #root.mainloop()
