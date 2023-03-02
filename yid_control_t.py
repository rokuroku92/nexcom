# -*- coding:utf-8 -*-
from tkinter import PhotoImage
import mqtt.publish_UI as mqt_pub
import Config
# YID 控制功能
# 模式切換變數
# mode_switch_status = 0 (自動), mode_switch_status = 1 (手動)
mode_switch_status = 0
# wh_status = 0 (正常), wh_status = 1 (異常)
wh_status = 0
wh_error_time = 0
# 模式切換 功能邏輯區------------------------------------------------
def mod_switch(btn_mode_str, btn_mode):
    global mode_switch_status
    mode_switch_status = 0 if mode_switch_status == 1 else 1
    img1 = PhotoImage(file=Config.img1)
    img4 = PhotoImage(file=Config.img4)
    print('切換為', '手動' if mode_switch_status == 1 else '自動',  '模式')

    if mode_switch_status == 1:
        btn_mode_str.set('手動')
        btn_mode.configure(image=img4)
        btn_mode.image = img4
    else:
        btn_mode_str.set('自動')
        btn_mode.configure(image=img1)
        btn_mode.image = img1

# 倉庫流道 功能邏輯區------------------------------------------------
def warehouse_status():
    global wh_status
    if wh_status == 1:
        global wh_error_time
        mqt_pub.publish("75", wh_error_time)


# 點選個站服務功能邏輯區------------------------------------------------
# station_id -> 站台 1 .. 6
# service_id -> 1: 箱件狀態,  2: 按鈕觸發, 3: 滾筒動作
# status_id -> 1: 有(轉動), 0: 無(停止)

station_name = {1: '站台 1', 2: '站台 2', 3: '站台 3', 4: '站台 4', 5: '站台 5', 6: '站台 6'}
service_name = {1: '箱件狀態', 2: '按鈕觸發', 3: '按鈕燈', 4: '滾筒動作'}
status_name = {1: '有(轉動)', 0: '無(停止)'}

def click_station_service(station_id, service_id, status_id, btn_trigger_1, btn_trigger_0):
    # 判斷是動手動模式，若是自動模式則直接離開此方法
    global mode_switch_status
    if mode_switch_status == 0:
        print('目前是自動模式')
        return  # 離開此方法

    img1 = PhotoImage(file=Config.img1)
    img2 = PhotoImage(file=Config.img2)

    if status_id == 1:
        btn_trigger_1.configure(image=img1)
        btn_trigger_1.image = img1
        btn_trigger_1.configure(fg="white")
        btn_trigger_0.configure(image=img2)
        btn_trigger_0.image = img2
        btn_trigger_0.configure(fg="black")
    else:
        btn_trigger_1.configure(image=img2)
        btn_trigger_1.image = img2
        btn_trigger_1.configure(fg="black")
        btn_trigger_0.configure(image=img1)
        btn_trigger_0.image = img1
        btn_trigger_0.configure(fg="white")


    print(station_id, service_id, status_id, end=' -> ')
    print(station_name[station_id], service_name[service_id], status_name[status_id])




