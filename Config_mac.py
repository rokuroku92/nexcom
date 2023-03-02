# -*- coding:utf-8 -*-

# MAC

# Mega2560 初始化
COM_PORT = '/dev/cu.usbserial-1420'
BAUD_RATE = 9600

# 建立資料庫連線
host = "localhost"
user = "root"
password = "12345678"
database = "YID"

# MQTT 初始化
address = "192.168.1.143"
port = 1883
topic_sub = "/missionA2C"  # 訂閱
topic_pub = "/missionC2A"  # 發送

# 定義圖片位址
img1 = 'image/btn_bg1.png'
img2 = 'image/btn_bg2.png'
img3 = 'image/yid_logo2.png'
img4 = 'image/btn_bg_red.png'
img_s1 = 'image/station1.png'
img_s2 = 'image/station2.png'
img_s3 = 'image/station3.png'
img_s4 = 'image/station4.png'
img_s5 = 'image/station5.png'
img_s6 = 'image/station6.png'
img_s1e = 'image/title_s1_error.png'
img_s2e = 'image/title_s2_error.png'
img_s3e = 'image/title_s3_error.png'
img_s4e = 'image/title_s4_error.png'
img_s5e = 'image/title_s5_error.png'
img_s6e = 'image/title_s6_error.png'

# 定義mp3位址
music_1 = "./mp3/ST1_error_sound.mp3"
music_2 = "./mp3/ST2_error_sound.mp3"
music_3 = "./mp3/ST3_error_sound.mp3"
music_4 = "./mp3/ST4_error_sound.mp3"
music_5 = "./mp3/ST5_error_sound.mp3"
music_6 = "./mp3/ST6_error_sound.mp3"
music_7 = "./mp3/WH_error_sound.mp3"
