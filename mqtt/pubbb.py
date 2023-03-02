# -*- coding:utf-8 -*-
import paho.mqtt.client as mqtt
import Config
class PublishUI():

    # 發佈
    def publish(self, data, timestamp):
        address = Config.address
        port = Config.port
        topic = Config.topic_sub
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
        client.will_set(topic=Config.topic_pub, qos=1)
        client.loop_start()
        # 發送字串

        station = int((int(data) - 1) / 10)
        cmd = int(data) % 10
        status = ''

        station = int(station)
        if int(cmd) == 1:
            cmd = 'transfer'
            status = "OK"
        elif int(cmd) == 5:
            cmd = 'error-fixed'
            status = "OK"
        elif int(cmd) == 2:
            cmd = 'roll-out'
        elif int(cmd) == 3:
            cmd = 'completed'
        elif int(cmd) == 4:
            cmd = 'error'
        if int(station) == 7:
            station = "warehouse"

        if status == '':
                msg = '{"cmd": "' + str(cmd) + '", "transfer_id": "' + timestamp + '", "station": "' + str(
                        station) + '"}'
        else :
                msg = '{"cmd": "' + str(cmd) + '", "transfer_id": "' + timestamp + '", "station": "' + str(
                        station) + '", "status": "' + status + '"}'
        print("發佈!!!!!!!!!!!!!!!!!: ", msg)
