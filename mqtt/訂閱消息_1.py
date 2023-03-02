import random
import time
from paho.mqtt import client as mqtt_client
import json
import pubbb
import threading

#broker = 'broker.emqx.io'
#broker = '127.0.0.1'
broker = '192.168.1.184'

port = 1883
topic = "/missionC2A"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
pub = pubbb.PublishUI()
i = 0
s1 = 0
s2 = 0
s3 = 0
s4 = 0
s5 = 0
s6 = 0
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    # msg = 得到訂閱訊息回應
    def on_message(client, userdata, msg):
        mystr = msg.payload.decode()  # 將 msg 解碼
        print("訂閱接收: " + msg.topic + " " + mystr)
        dict = json.loads(mystr)  # 將 str 轉 dict 格式
        cmd = dict['cmd'].strip()  # 去除左右空白 .strip()
        station = dict['station'].strip()
        timestamp = dict['transfer_id'].strip()
        status = dict['status'].strip()
        print('訂閱接收(分析 json 字串):', timestamp, cmd, station, status)
        if cmd == 'transfer':
            cmd = 1
        elif cmd == 'roll-out':
            cmd = 2
        elif cmd == 'completed':
            cmd = 3
        elif cmd == 'error':
            cmd = 4
        elif cmd == 'error-fixed':
            cmd = 5
        else:
            cmd = 8

        #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if cmd == 1:
            pub.publish(str(station)+str(1), timestamp)
            if int(station) == 1:
                global s1
                s1 = timestamp
            elif int(station) == 2:
                global s2
                s2 = timestamp
            elif int(station) == 3:
                global s3
                s3 = timestamp
            elif int(station) == 4:
                global s4
                s4 = timestamp
            elif int(station) == 5:
                global s5
                s5 = timestamp
            elif int(station) == 6:
                global s6
                s6 = timestamp
            time.sleep(1)
        # elif cmd == 2:
        #     global i
        #     if i % 2 == 0:
        #         pub.publish(str(station) + str(4), timestamp)
        #         i += 1
        #     else:
        #         pub.publish(str(station) + str(3), timestamp)
        #         i += 1
        # elif cmd == 5:
        #     pub.publish(str(station) + str(5), timestamp)
        #     time.sleep(1)
        #     pub.publish(str(station)+str(2), timestamp)
        #     time.sleep(5)
        #     pub.publish(str(station) + str(3), timestamp)



    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

def startmqttthread():
    print('mqtt')
    # 啟動訂閱服務執行緒
    mqttthread = threading.Thread(target=startwork)
    mqttthread.start()

def startwork():
    while True:
        global s1
        global s2
        global s3
        global s4
        global s5
        global s6
        if s1 != 0:
            time.sleep(1)
            pub.publish(str(1) + str(2), s1)
            time.sleep(6)
            pub.publish(str(1) + str(3), s1)
            s1 = 0
        elif s2 != 0:
            time.sleep(1)
            pub.publish(str(2) + str(2), s2)
            time.sleep(6)
            pub.publish(str(2) + str(3), s2)
            s2 = 0
        elif s3 != 0:
            time.sleep(1)
            pub.publish(str(3) + str(2), s3)
            time.sleep(6)
            pub.publish(str(3) + str(3), s3)
            s3 = 0
        elif s4 != 0:
            time.sleep(1)
            pub.publish(str(4) + str(2), s4)
            time.sleep(6)
            pub.publish(str(4) + str(3), s4)
            s4 = 0
        elif s5 != 0:
            time.sleep(1)
            pub.publish(str(5) + str(2), s5)
            time.sleep(6)
            pub.publish(str(5) + str(3), s5)
            s5 = 0
        elif s6 != 0:
            time.sleep(1)
            pub.publish(str(6) + str(2), s6)
            time.sleep(6)
            pub.publish(str(6) + str(3), s6)
            s6 = 0
        print("check")
        time.sleep(1)


if __name__ == '__main__':
    startmqttthread()
    run()
