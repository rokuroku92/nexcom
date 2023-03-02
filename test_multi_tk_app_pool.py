# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import PhotoImage, font, messagebox
import serial
import threading
import os
import yid_control_t
from yid_util import get_ip_address, getCPUuse
from yid_control_t import mod_switch, warehouse_status, click_station_service
import mqtt.publish_UI as mqt_pub
from datetime import datetime
import mysql.connector
from mysql.connector import pooling
import json
import paho.mqtt.client as mqtt
import time
from pygame import mixer
import Config
import random
import Conn


class App:
    # Mega2560 初始化
    COM_PORT = Config.COM_PORT
    BAUD_RATE = Config.BAUD_RATE

    # 建立資料庫連線
    # mydb_pool = Conn.get_mydb_pool()
    # mydb = mydb_pool.get_connection()
    # mycursor = mydb.cursor(buffered=True)

    # MQTT 初始化
    address = Config.address
    port = Config.port
    topic = Config.topic_sub

    error_time = 0
    error_station = 0
    music_loop = 0
    iLink = 0

    def __init__(self, root):
        # 主程式開始
        root.title('YID ')  # 設定 UI 標題，並加上本機 IP 位址
        root.geometry('1024x600')  # 設定 UI 畫素尺寸
        self.myfont = font.Font(family='Microsoft JhengHei', size=16, weight='normal')  # 定義一般字型，簡化後續coding
        self.myfont_st = font.Font(family='Helvetica', size=30, weight='bold')  # 定義小標字型，簡化後續coding
        self.img1 = PhotoImage(file=Config.img1)  # 定義 第 1 類 按鈕引用圖片，簡化後續coding
        self.img2 = PhotoImage(file=Config.img2)  # 定義 第 2 類 按鈕引用圖片，簡化後續coding
        self.img3 = PhotoImage(file=Config.img3)  # 定義 LOGO + 系統名稱 引用圖片，簡化後續coding
        self.img4 = PhotoImage(file=Config.img4)  # 定義異常按鈕引用圖片，簡化後續coding
        self.img_s1 = PhotoImage(file=Config.img_s1)  # 定義 第1站 名稱 引用圖片，簡化後續coding
        self.img_s2 = PhotoImage(file=Config.img_s2)  # 定義 第2站 名稱 引用圖片，簡化後續coding
        self.img_s3 = PhotoImage(file=Config.img_s3)  # 定義 第3站 名稱 引用圖片，簡化後續coding
        self.img_s4 = PhotoImage(file=Config.img_s4)  # 定義 第4站 名稱 引用圖片，簡化後續coding
        self.img_s5 = PhotoImage(file=Config.img_s5)  # 定義 第5站 名稱 引用圖片，簡化後續coding
        self.img_s6 = PhotoImage(file=Config.img_s6)  # 定義 第6站 名稱 引用圖片，簡化後續coding
        self.img_s1e = PhotoImage(file=Config.img_s1e)  # error image
        self.img_s2e = PhotoImage(file=Config.img_s2e)  # error image
        self.img_s3e = PhotoImage(file=Config.img_s3e)  # error image
        self.img_s4e = PhotoImage(file=Config.img_s4e)  # error image
        self.img_s5e = PhotoImage(file=Config.img_s5e)  # error image
        self.img_s6e = PhotoImage(file=Config.img_s6e)  # error image

        # View 元件佈局
        root.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), weight=1)  # 列 0  列 1 同步放大縮小
        root.columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)  # 欄 0, 欄 1, 欄 2 同步放大縮小

        # View 元件
        # -----Logo、模式切換、連線狀態、倉庫狀態等UI架構-------------------------------------------------------
        self.label_logo = tk.Label(image=self.img3)  # 定義 logo 格式為 Label，並引用圖片
        self.label_mode = tk.Label(text='模式切換', font=self.myfont)  # 定義 模式切換 格式為 Label，並設定顯示內容與字型
        self.label_linkage = tk.Label(text='連線狀態', font=self.myfont)
        self.label_warehouse = tk.Label(text='倉庫流道', font=self.myfont)

        self.btn_mode_str = tk.StringVar()  # 定義 self.btn_mode_str 為 TK 字串變數
        self.btn_mode_str.set("自動")  # 預設填入文字為 "自動"
        self.btn_mode = tk.Label(textvariable=self.btn_mode_str, font=self.myfont, image=self.img1, compound='center', fg="white")
        # 設定 模式切換 按鈕的顯示方式，特別注意 文字變數 的引用
        self.btn_mode.bind("<Button-1>", lambda e: mod_switch(self.btn_mode_str, self.btn_mode))
        # 由於不希望出現框限，故前列將 顯示型態 設定為 Label，但因本質上還是按鈕，故引用 外加按鈕 定義攻勢，須注意 要 def 相對應的function

        self.btn_linkage_str = tk.StringVar()
        self.btn_linkage_str.set("離線")
        self.btn_linkage = tk.Label(textvariable=self.btn_linkage_str, font=self.myfont, image=self.img4, compound='center', fg="white")

        self.btn_warehouse_str = tk.StringVar()
        self.btn_warehouse_str.set("正常")
        self.btn_warehouse = tk.Label(textvariable=self.btn_warehouse_str, font=self.myfont, image=self.img1, compound='center', fg="white")
        self.btn_warehouse.bind("<Button-1>", lambda e: warehouse_status())

        self.label_logo.grid(row=0, column=0, rowspan=8, columnspan=2, sticky='EWNS')  # sticky='EWNS' 無縫填滿
        # 設定 logo 顯示的 左上角起始位置、所佔列高(8)、所佔行寬(2)
        self.label_logo.bind("<Button-1>", lambda e: self.shutdownConfirm())

        self.label_mode.grid(row=9, column=0, sticky='EWNS')  # 設定 模式切換 標籤 顯示的位置與配置原則 無縫填滿
        self.btn_mode.grid(row=9, column=1, sticky='EWNS')  # 設定 模式切換 按鈕 顯示的位置與配置原則 無縫填滿

        self.label_linkage.grid(row=10, column=0, sticky='EWNS')
        self.btn_linkage.grid(row=10, column=1, sticky='EWNS')

        self.label_warehouse.grid(row=11, column=0, sticky='EWNS')
        self.btn_warehouse.grid(row=11, column=1, sticky='EWNS')
        # -----第 1 站UI架構-------------------------------------------------------------------------------

        self.label_station1 = tk.Label(image=self.img_s1, compound='left', bg='white')
        self.label_box = tk.Label(text='箱件狀態', font=self.myfont, bg='white')
        self.label_trigger = tk.Label(text='按鈕觸發', font=self.myfont, bg='white')
        self.label_roller = tk.Label(text='滾筒動作', font=self.myfont, bg='white')

        self.btn_box_1_1 = tk.Label(text='有箱', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_box_1_0 = tk.Label(text='無箱', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")
        self.btn_trigger_1_1 = tk.Label(text='有', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_trigger_1_0 = tk.Label(text='無', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")
        self.btn_roller_1_1 = tk.Label(text='轉動', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_roller_1_0 = tk.Label(text='停止', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")

        self.btn_trigger_1_1.bind("<Button-1>",
                                  lambda e: [click_station_service(1, 2, 1, self.btn_trigger_1_1, self.btn_trigger_1_0), self.send("131")])
        self.btn_trigger_1_0.bind("<Button-1>",
                             lambda e: [click_station_service(1, 2, 0, self.btn_trigger_1_1, self.btn_trigger_1_0), self.send("130")])
        self.btn_roller_1_1.bind("<Button-1>",
                            lambda e: [click_station_service(1, 4, 1, self.btn_roller_1_1, self.btn_roller_1_0), self.send("141")])
        self.btn_roller_1_0.bind("<Button-1>",
                                lambda e: [click_station_service(1, 4, 0, self.btn_roller_1_1, self.btn_roller_1_0), self.send("140")])

        self.label_station1.grid(row=0, column=2, columnspan=3, sticky='EWNS')  # sticky='EWNS' 無縫填滿

        self.label_box.grid(row=1, column=2, sticky='EWNS')
        self.btn_box_1_1.grid(row=1, column=3, sticky='EWNS')
        self.btn_box_1_0.grid(row=1, column=4, sticky='EWNS')

        self.label_trigger.grid(row=2, column=2, sticky='EWNS')
        self.btn_trigger_1_1.grid(row=2, column=3, sticky='EWNS')
        self.btn_trigger_1_0.grid(row=2, column=4, sticky='EWNS')

        self.label_roller.grid(row=3, column=2, sticky='EWNS')
        self.btn_roller_1_1.grid(row=3, column=3, sticky='EWNS')
        self.btn_roller_1_0.grid(row=3, column=4, sticky='EWNS')

        # -----第 2 站UI架構-------------------------------------------------------------------

        self.label_station2 = tk.Label(image=self.img_s2, compound='left', bg='white')
        self.label_box = tk.Label(text='箱件狀態', font=self.myfont, bg='white')
        self.label_trigger = tk.Label(text='按鈕觸發', font=self.myfont, bg='white')
        self.label_roller = tk.Label(text='滾筒動作', font=self.myfont, bg='white')

        self.btn_box_2_1 = tk.Label(text='有箱', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_box_2_0 = tk.Label(text='無箱', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")
        self.btn_trigger_2_1 = tk.Label(text='有', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_trigger_2_0 = tk.Label(text='無', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")
        self.btn_roller_2_1 = tk.Label(text='轉動', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_roller_2_0 = tk.Label(text='停止', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")

        self.btn_trigger_2_1.bind("<Button-1>",
                             lambda e: [click_station_service(2, 2, 1, self.btn_trigger_2_1, self.btn_trigger_2_0), self.send("231")])
        self.btn_trigger_2_0.bind("<Button-1>",
                             lambda e: [click_station_service(2, 2, 0, self.btn_trigger_2_1, self.btn_trigger_2_0), self.send("230")])
        self.btn_roller_2_1.bind("<Button-1>",
                            lambda e: [click_station_service(2, 4, 1, self.btn_roller_2_1, self.btn_roller_2_0), self.send("241")])
        self.btn_roller_2_0.bind("<Button-1>",
                            lambda e: [click_station_service(2, 4, 0, self.btn_roller_2_1, self.btn_roller_2_0), self.send("240")])

        self.label_station2.grid(row=4, column=2, columnspan=3, sticky='EWNS')  # sticky='EWNS' 無縫填滿

        self.label_box.grid(row=5, column=2, sticky='EWNS')
        self.btn_box_2_1.grid(row=5, column=3, sticky='EWNS')
        self.btn_box_2_0.grid(row=5, column=4, sticky='EWNS')

        self.label_trigger.grid(row=6, column=2, sticky='EWNS')
        self.btn_trigger_2_1.grid(row=6, column=3, sticky='EWNS')
        self.btn_trigger_2_0.grid(row=6, column=4, sticky='EWNS')

        self.label_roller.grid(row=7, column=2, sticky='EWNS')
        self.btn_roller_2_1.grid(row=7, column=3, sticky='EWNS')
        self.btn_roller_2_0.grid(row=7, column=4, sticky='EWNS')

        # ------第 3 站UI架構--------------------------------------------------------------------

        self.label_station3 = tk.Label(image=self.img_s3, compound='left', bg='white')
        self.label_box = tk.Label(text='箱件狀態', font=self.myfont, bg='white')
        self.label_trigger = tk.Label(text='按鈕觸發', font=self.myfont, bg='white')
        self.label_roller = tk.Label(text='滾筒動作', font=self.myfont, bg='white')

        self.btn_box_3_1 = tk.Label(text='有箱', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_box_3_0 = tk.Label(text='無箱', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")
        self.btn_trigger_3_1 = tk.Label(text='有', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_trigger_3_0 = tk.Label(text='無', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")
        self.btn_roller_3_1 = tk.Label(text='轉動', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_roller_3_0 = tk.Label(text='停止', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")

        self.btn_trigger_3_1.bind("<Button-1>",
                             lambda e: [click_station_service(3, 2, 1, self.btn_trigger_3_1, self.btn_trigger_3_0), self.send("331")])
        self.btn_trigger_3_0.bind("<Button-1>",
                             lambda e: [click_station_service(3, 2, 0, self.btn_trigger_3_1, self.btn_trigger_3_0), self.send("330")])
        self.btn_roller_3_1.bind("<Button-1>",
                            lambda e: [click_station_service(3, 4, 1, self.btn_roller_3_1, self.btn_roller_3_0), self.send("341")])
        self.btn_roller_3_0.bind("<Button-1>",
                            lambda e: [click_station_service(3, 4, 0, self.btn_roller_3_1, self.btn_roller_3_0), self.send("340")])

        self.label_station3.grid(row=8, column=2, columnspan=3, sticky='EWNS')  # sticky='EWNS' 無縫填滿

        self.label_box.grid(row=9, column=2, sticky='EWNS')
        self.btn_box_3_1.grid(row=9, column=3, sticky='EWNS')
        self.btn_box_3_0.grid(row=9, column=4, sticky='EWNS')

        self.label_trigger.grid(row=10, column=2, sticky='EWNS')
        self.btn_trigger_3_1.grid(row=10, column=3, sticky='EWNS')
        self.btn_trigger_3_0.grid(row=10, column=4, sticky='EWNS')

        self.label_roller.grid(row=11, column=2, sticky='EWNS')
        self.btn_roller_3_1.grid(row=11, column=3, sticky='EWNS')
        self.btn_roller_3_0.grid(row=11, column=4, sticky='EWNS')

        # -----第 4 站UI架構----------------------------------------------------------------------

        self.label_station4 = tk.Label(image=self.img_s4, compound='left', bg='white')
        self.label_box = tk.Label(text='箱件狀態', font=self.myfont, bg='white')
        self.label_trigger = tk.Label(text='按鈕觸發', font=self.myfont, bg='white')
        self.label_roller = tk.Label(text='滾筒動作', font=self.myfont, bg='white')

        self.btn_box_4_1 = tk.Label(text='有箱', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_box_4_0 = tk.Label(text='無箱', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")
        self.btn_trigger_4_1 = tk.Label(text='有', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_trigger_4_0 = tk.Label(text='無', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")
        self.btn_roller_4_1 = tk.Label(text='轉動', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_roller_4_0 = tk.Label(text='停止', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")

        self.btn_trigger_4_1.bind("<Button-1>",
                             lambda e: [click_station_service(4, 2, 1, self.btn_trigger_4_1, self.btn_trigger_4_0), self.send("431")])
        self.btn_trigger_4_0.bind("<Button-1>",
                             lambda e: [click_station_service(4, 2, 0, self.btn_trigger_4_1, self.btn_trigger_4_0), self.send("430")])
        self.btn_roller_4_1.bind("<Button-1>",
                            lambda e: [click_station_service(4, 4, 1, self.btn_roller_4_1, self.btn_roller_4_0), self.send("441")])
        self.btn_roller_4_0.bind("<Button-1>",
                            lambda e: [click_station_service(4, 4, 0, self.btn_roller_4_1, self.btn_roller_4_0), self.send("440")])

        self.label_station4.grid(row=0, column=5, columnspan=3, sticky='EWNS')  # sticky='EWNS' 無縫填滿

        self.label_box.grid(row=1, column=5, sticky='EWNS')
        self.btn_box_4_1.grid(row=1, column=6, sticky='EWNS')
        self.btn_box_4_0.grid(row=1, column=7, sticky='EWNS')

        self.label_trigger.grid(row=2, column=5, sticky='EWNS')
        self.btn_trigger_4_1.grid(row=2, column=6, sticky='EWNS')
        self.btn_trigger_4_0.grid(row=2, column=7, sticky='EWNS')

        self.label_roller.grid(row=3, column=5, sticky='EWNS')
        self.btn_roller_4_1.grid(row=3, column=6, sticky='EWNS')
        self.btn_roller_4_0.grid(row=3, column=7, sticky='EWNS')

        # ------第 5 站UI架構------------------------------------------------------------------------

        self.label_station5 = tk.Label(image=self.img_s5, compound='left', bg='white')
        self.label_box = tk.Label(text='箱件狀態', font=self.myfont, bg='white')
        self.label_trigger = tk.Label(text='按鈕觸發', font=self.myfont, bg='white')
        self.label_roller = tk.Label(text='滾筒動作', font=self.myfont, bg='white')

        self.btn_box_5_1 = tk.Label(text='有箱', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_box_5_0 = tk.Label(text='無箱', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")
        self.btn_trigger_5_1 = tk.Label(text='有', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_trigger_5_0 = tk.Label(text='無', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")
        self.btn_roller_5_1 = tk.Label(text='轉動', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_roller_5_0 = tk.Label(text='停止', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")

        self.btn_trigger_5_1.bind("<Button-1>",
                             lambda e: [click_station_service(5, 2, 1, self.btn_trigger_5_1, self.btn_trigger_5_0), self.send("531")])
        self.btn_trigger_5_0.bind("<Button-1>",
                             lambda e: [click_station_service(5, 2, 0, self.btn_trigger_5_1, self.btn_trigger_5_0), self.send("530")])
        self.btn_roller_5_1.bind("<Button-1>",
                            lambda e: [click_station_service(5, 4, 1, self.btn_roller_5_1, self.btn_roller_5_0), self.send("541")])
        self.btn_roller_5_0.bind("<Button-1>",
                            lambda e: [click_station_service(5, 4, 0, self.btn_roller_5_1, self.btn_roller_5_0), self.send("540")])

        self.label_station5.grid(row=4, column=5, columnspan=3, sticky='EWNS')  # sticky='EWNS' 無縫填滿

        self.label_box.grid(row=5, column=5, sticky='EWNS')
        self.btn_box_5_1.grid(row=5, column=6, sticky='EWNS')
        self.btn_box_5_0.grid(row=5, column=7, sticky='EWNS')

        self.label_trigger.grid(row=6, column=5, sticky='EWNS')
        self.btn_trigger_5_1.grid(row=6, column=6, sticky='EWNS')
        self.btn_trigger_5_0.grid(row=6, column=7, sticky='EWNS')

        self.label_roller.grid(row=7, column=5, sticky='EWNS')
        self.btn_roller_5_1.grid(row=7, column=6, sticky='EWNS')
        self.btn_roller_5_0.grid(row=7, column=7, sticky='EWNS')

        # -----第 6 站UI架構------------------------------------------------------------------------

        self.label_station6 = tk.Label(image=self.img_s6, compound='left', bg='white')
        self.label_box = tk.Label(text='箱件狀態', font=self.myfont, bg='white')
        self.label_trigger = tk.Label(text='按鈕觸發', font=self.myfont, bg='white')
        self.label_roller = tk.Label(text='滾筒動作', font=self.myfont, bg='white')

        self.btn_box_6_1 = tk.Label(text='有箱', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_box_6_0 = tk.Label(text='無箱', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")
        self.btn_trigger_6_1 = tk.Label(text='有', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_trigger_6_0 = tk.Label(text='無', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")
        self.btn_roller_6_1 = tk.Label(text='轉動', font=self.myfont, image=self.img2, compound='center', bg='white')
        self.btn_roller_6_0 = tk.Label(text='停止', font=self.myfont, image=self.img1, compound='center', bg='white', fg="white")

        self.btn_trigger_6_1.bind("<Button-1>",
                             lambda e: [click_station_service(6, 2, 1, self.btn_trigger_6_1, self.btn_trigger_6_0), self.send("631")])
        self.btn_trigger_6_0.bind("<Button-1>",
                             lambda e: [click_station_service(6, 2, 0, self.btn_trigger_6_1, self.btn_trigger_6_0), self.send("630")])
        self.btn_roller_6_1.bind("<Button-1>",
                            lambda e: [click_station_service(6, 4, 1, self.btn_roller_6_1, self.btn_roller_6_0), self.send("641")])
        self.btn_roller_6_0.bind("<Button-1>",
                            lambda e: [click_station_service(6, 4, 0, self.btn_roller_6_1, self.btn_roller_6_0), self.send("640")])

        self.label_station6.grid(row=8, column=5, columnspan=3, sticky='EWNS')  # sticky='EWNS' 無縫填滿

        self.label_box.grid(row=9, column=5, sticky='EWNS')
        self.btn_box_6_1.grid(row=9, column=6, sticky='EWNS')
        self.btn_box_6_0.grid(row=9, column=7, sticky='EWNS')

        self.label_trigger.grid(row=10, column=5, sticky='EWNS')
        self.btn_trigger_6_1.grid(row=10, column=6, sticky='EWNS')
        self.btn_trigger_6_0.grid(row=10, column=7, sticky='EWNS')

        self.label_roller.grid(row=11, column=5, sticky='EWNS')
        self.btn_roller_6_1.grid(row=11, column=6, sticky='EWNS')
        self.btn_roller_6_0.grid(row=11, column=7, sticky='EWNS')
     
        # 執行緒載入
        time.sleep(1)
        self.startpingthread()  # PING
        time.sleep(1)
        self.startmqttthread()  # MQTT
        self.checkdbthread()  # Check DB
        # time.sleep(1)
        self.startmp3thread()  # MP3
        # self.dbthread()  # db check

        root.mainloop()

    def send(self, send_data):
        # threading.Event().wait(random.random())
        time.sleep(random.random())
        # 給UI手自動模式專用
        timestamp = (datetime.now().strftime('%Y%m%d%H%M%S%f'))  # 製造時間戳記
        if yid_control_t.mode_switch_status == 1:
            if send_data == "131":
                mqt_pub.publish('11', timestamp)
            elif send_data == "231":
                mqt_pub.publish('21', timestamp)
            elif send_data == "331":
                mqt_pub.publish('31', timestamp)
            elif send_data == "431":
                mqt_pub.publish('41', timestamp)
            elif send_data == "531":
                mqt_pub.publish('51', timestamp)
            elif send_data == "631":
                mqt_pub.publish('61', timestamp)
            elif send_data == "141":
                print("1roll-out!!!!!!!!!!!!!!!!!!!")
                threading.Event().wait(4)
                self.btn_roller_1_1.configure(image=self.img2)
                self.btn_roller_1_1.image = self.img2
                self.btn_roller_1_1.configure(fg="black")
                self.btn_roller_1_0.configure(image=self.img1)
                self.btn_roller_1_0.image = self.img1
                self.btn_roller_1_0.configure(fg="white")
            elif send_data == "241":
                print("2roll-out!!!!!!!!!!!!!!!!!!!")
                threading.Event().wait(4)
                self.btn_roller_2_1.configure(image=self.img2)
                self.btn_roller_2_1.image = self.img2
                self.btn_roller_2_1.configure(fg="black")
                self.btn_roller_2_0.configure(image=self.img1)
                self.btn_roller_2_0.image = self.img1
                self.btn_roller_2_0.configure(fg="white")
            elif send_data == "341":
                print("3roll-out!!!!!!!!!!!!!!!!!!!")
                threading.Event().wait(4)
                self.btn_roller_3_1.configure(image=self.img2)
                self.btn_roller_3_1.image = self.img2
                self.btn_roller_3_1.configure(fg="black")
                self.btn_roller_3_0.configure(image=self.img1)
                self.btn_roller_3_0.image = self.img1
                self.btn_roller_3_0.configure(fg="white")
            elif send_data == "441":
                print("4roll-out!!!!!!!!!!!!!!!!!!!")
                self.btn_roller_4_1.configure(image=self.img2)
                self.btn_roller_4_1.image = self.img2
                self.btn_roller_4_1.configure(fg="black")
                self.btn_roller_4_0.configure(image=self.img1)
                self.btn_roller_4_0.image = self.img1
                self.btn_roller_4_0.configure(fg="white")
                threading.Event().wait(4)
            elif send_data == "541":
                print("5roll-out!!!!!!!!!!!!!!!!!!!")
                threading.Event().wait(4)
                self.btn_roller_5_1.configure(image=self.img2)
                self.btn_roller_5_1.image = self.img2
                self.btn_roller_5_1.configure(fg="black")
                self.btn_roller_5_0.configure(image=self.img1)
                self.btn_roller_5_0.image = self.img1
                self.btn_roller_5_0.configure(fg="white")
            elif send_data == "641":
                print("6roll-out!!!!!!!!!!!!!!!!!!!")
                threading.Event().wait(4)
                self.btn_roller_6_1.configure(image=self.img2)
                self.btn_roller_6_1.image = self.img2
                self.btn_roller_6_1.configure(fg="black")
                self.btn_roller_6_0.configure(image=self.img1)
                self.btn_roller_6_0.image = self.img1
                self.btn_roller_6_0.configure(fg="white")
    def sendM(self, send_data):
        # 給MQTT專用的
        print("send: ", send_data)


    # MQTT
    # 訂閱內容處理
    def startmqttthread(self):
        print('mqtt')
        # 啟動訂閱服務執行緒
        mqttthread = threading.Thread(target=self.sub)
        mqttthread.start()

    def handle_msg(self, msg):
        try:
                mystr = str(msg.payload.decode())
                print("訂閱接收: " + msg.topic + " " + mystr)
                # 分析 json 字串
                dict = json.loads(mystr)  # 將 str 轉 dict 格式
                cmd = dict['cmd'].strip()  # 去除左右空白 .strip()
                station = dict['station'].strip()
                timestamp = dict['transfer_id'].strip()
                try:
                        status = dict['status'].strip()
                except :
                        status = ""
                print('訂閱接收(分析 json 字串):', timestamp, type(timestamp), cmd, type(cmd), station, type(station))

                if cmd == 'transfer':
                    cmd = 1
                elif cmd == 'roll-out':
                    cmd = 2
                elif cmd == 'completed':
                    cmd = 3
                elif cmd == 'error':
                    cmd = 4
                    self.error_time = timestamp  # 將錯誤時間紀錄並在error-fixed時回傳
                elif cmd == 'error-fixed':
                    cmd = 5
                else:
                    cmd = 8
                if station == 'warehouse':
                    station = 7
                
                mydb = Conn.get_mydb_pool().get_connection()
                mycursor = mydb.cursor()

                if ((int(cmd) == 2) | (int(cmd) == 3) | (int(cmd) == 4)) & (int(station) != 7):
                    # 先查詢DB資料各站點最後一列資料是否重複
                    sql = "SELECT cmd_id,timestamp_id FROM a2c ORDER BY a2c_id DESC LIMIT 1"
                    mycursor.execute(sql)
                    result = mycursor.fetchone()
                    # 時間或命令不相同時則記入DB
                    if (str(result[1]) != str(timestamp)) | (str(result[0]) != str(cmd)):
                        # 新增 a2c
                        sql = "INSERT INTO a2c (timestamp_id, station_id, ack_handshaking, cmd_id) VALUES (%s, %s, %s, %s)"
                        val = (timestamp, station, "C", cmd)
                        mycursor.execute(sql, val)
                        mydb.commit()
                        # 判斷命令發送指令給MEGA2560
                        if int(cmd) == 2:
                            x = str(station) + "41"
                            self.sendM(x)
                        elif int(cmd) == 3:
                            x = str(station) + "30"
                            self.sendM(x)
                        elif int(cmd) == 4:
                            x = str(station) + "51"
                            self.sendM(x)
                            self.error_station = station
                            if int(station) == 1:
                                self.label_station1.configure(image=self.img_s1e)
                                self.label_station1.image = self.img_s1e
                            elif int(station) == 2:
                                self.label_station2.configure(image=self.img_s2e)
                                self.label_station2.image = self.img_s2e
                            elif int(station) == 3:
                                self.label_station3.configure(image=self.img_s3e)
                                self.label_station3.image = self.img_s3e
                            elif int(station) == 4:
                                self.label_station4.configure(image=self.img_s4e)
                                self.label_station4.image = self.img_s4e
                            elif int(station) == 5:
                                self.label_station5.configure(image=self.img_s5e)
                                self.label_station5.image = self.img_s5e
                            elif int(station) == 6:
                                self.label_station6.configure(image=self.img_s6e)
                                self.label_station6.image = self.img_s6e
                    # 不管資料有無重複都會回傳OK
                    self.publish(str(str(station) + str(cmd)), timestamp)
                    # 新增 log
                    sql = "INSERT INTO log (timestamp_id, station_id, ack_handshaking, cmd_id) VALUES (%s, %s, %s, %s)"
                    val = (timestamp, station, "C", cmd)
                    mycursor.execute(sql, val)
                    mydb.commit()

                elif ((int(cmd) == 1) | (int(cmd) == 5)) & (int(station) != 7):
                    if status == 'OK':
                        # 回寫 c2a ack_handshaking
                        sql = "SELECT c2a_id FROM c2a where c2a_id in(select max(c2a_id) from c2a where station_id= " + str(int(station)) + ")"
                        mycursor.execute(sql)
                        c2a_id = mycursor.fetchone()
                        print(c2a_id)
                        c2a_id = str(c2a_id).strip("'").strip("(").strip(")").replace(",", "")
                        print(c2a_id, type(c2a_id))
                        sql = "update c2a set ack_handshaking = 'A' where c2a_id = " + str(c2a_id)
                        print(sql)
                        mycursor.execute(sql)
                        mydb.commit()

                       # 判斷命令發送指令給MEGA2560
                        sql = "SELECT cmd_id,timestamp_id FROM a2c ORDER BY a2c_id DESC LIMIT 1"
                        mycursor.execute(sql)
                        result = mycursor.fetchone()
                        if (str(result[1]) != str(timestamp)) | (str(result[0]) != str(cmd)):
                            if int(cmd) == 1:
                                x = str(station) + "31"
                                self.sendM(x)
                            elif int(cmd) == 5:
                                x = str(station) + "61"
                                self.sendM(x)
                                self.error_station = 0
                                self.music_loop = 0
                                if int(station) == 1:
                                    self.label_station1.configure(image=self.img_s1)
                                    self.label_station1.image = self.img_s1
                                elif int(station) == 2:
                                    self.label_station2.configure(image=self.img_s2)
                                    self.label_station2.image = self.img_s2
                                elif int(station) == 3:
                                    self.label_station3.configure(image=self.img_s3)
                                    self.label_station3.image = self.img_s3
                                elif int(station) == 4:
                                    self.label_station4.configure(image=self.img_s4)
                                    self.label_station4.image = self.img_s4
                                elif int(station) == 5:
                                    self.label_station5.configure(image=self.img_s5)
                                    self.label_station5.image = self.img_s5
                                elif int(station) == 6:
                                    self.label_station6.configure(image=self.img_s6)
                                    self.label_station6.image = self.img_s6
                        # 新增 log
                        sql = "INSERT INTO log (timestamp_id, station_id, ack_handshaking, cmd_id) VALUES (%s, %s, %s, %s)"
                        val = (timestamp, station, "A", cmd)
                        mycursor.execute(sql, val)
                        mydb.commit()
                elif station == 7:
                    # 先查詢DB資料倉庫的最後一列資料是否重複
                    sql = "SELECT cmd_id,timestamp_id FROM warehouse_error ORDER BY warehouse_error_id DESC LIMIT 1"
                    mycursor.execute(sql)
                    result = mycursor.fetchone()
                    if (str(result[1]) != str(timestamp)) | (str(result[0]) != str(cmd)):
                        # 新增 warehouse_error
                        if cmd == 4:
                            self.btn_warehouse_str.set("異常")
                            self.btn_warehouse.configure(image=self.img4)
                            self.btn_warehouse.image = self.img4
                            self.btn_warehouse.configure(fg="white")
                            self.error_station = station
                            yid_control_t.wh_status = 1
                            yid_control_t.wh_error_time = timestamp
                            sql = "INSERT INTO warehouse_error (timestamp_id, station_id, ack_handshaking, cmd_id) VALUES (%s, %s, %s, %s)"
                            val = (timestamp, station, "C", cmd)
                            mycursor.execute(sql, val)
                            mydb.commit()
                            self.publish(str(str(station) + str(cmd)), timestamp)
                            # 新增 log
                            sql = "INSERT INTO log (timestamp_id, station_id, ack_handshaking, cmd_id) VALUES (%s, %s, %s, %s)"
                            val = (timestamp, station, "C", cmd)
                            mycursor.execute(sql, val)
                    if status == 'OK':
                        self.btn_warehouse_str.set("正常")
                        self.btn_warehouse.configure(image=self.img1)
                        self.btn_warehouse.image = self.img1
                        self.btn_warehouse.configure(fg="white")
                        yid_control_t.wh_status = 0
                        self.error_station = 0
                        self.music_loop = 0
                        # 回寫 ack_handshaking
                        sql = "SELECT warehouse_error_id FROM warehouse_error ORDER BY warehouse_error_id DESC LIMIT 1"
                        mycursor.execute(sql)
                        warehouse_error_id = mycursor.fetchone()
                        warehouse_error_id = str(warehouse_error_id).strip("'").strip("(").strip(")").replace(",", "")
                        print(warehouse_error_id, type(warehouse_error_id))
                        sql = "update warehouse_error set ack_handshaking = 'A' where warehouse_error_id = " + str(warehouse_error_id)
                        print(sql)
                        mycursor.execute(sql)
                        mydb.commit()
                        # 新增 log
                        sql = "INSERT INTO log (timestamp_id, station_id, ack_handshaking, cmd_id) VALUES (%s, %s, %s, %s)"
                        val = (timestamp, station, "A", cmd)
                        mycursor.execute(sql, val)
                    mydb.commit()
                else:
                    print("Command error")
                mydb.close()
                mycursor.close()
        except Exception as e:
                print(e)

    # 訂閱
    def sub(self):
        try:
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
        except Exception as e:
            print("sub error:", e)

    # 發佈
    def publish(self, data, timestamp):
        try:
            address = Config.address
            port = Config.port
            topic = Config.topic_pub
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


            if str(int(cmd)) == '2':
                cmd = 'roll-out'
                status = 'OK'
            elif str(int(cmd)) == '3':
                cmd = 'completed'
                status = 'OK'
            elif str(int(cmd)) == '4':
                cmd = 'error'
                status = 'OK'
            if str(int(station)) == '7':
                station = 'warehouse'
            else:
                station = int(station)
            if status == '':
                msg = '{"cmd": "' + str(cmd) + '", "transfer_id": "' + timestamp + '", "station": "' + str(
                        station) + '"}'
            else :
                msg = '{"cmd": "' + str(cmd) + '", "transfer_id": "' + timestamp + '", "station": "' + str(
                        station) + '", "status": "' + status + '"}'
            client.publish(topic, payload=msg, qos=0)
        except Exception as e:
            print("pub error:", e)

    def checkdbthread(self):
        print('check db')
        cdbthread = threading.Thread(target=self.check_db_loop)
        cdbthread.start()

    #  檢查db最後一行的ack_handshaking
    def check_db_loop(self):
        while True:
            try:
                mydb = Conn.get_mydb_pool().get_connection()
                mycursor = mydb.cursor()
                for i in range(1, 7):
                    sql = "select a.station_id,a.cmd_id,a.ack_handshaking,a.timestamp_id from " \
                          "YID.c2a a where a.c2a_id in (SELECT max(a.c2a_id) FROM YID.c2a a group by a.station_id) and station_id= "+str(i)+";"
                    mycursor.execute(sql)
                    result = mycursor.fetchone()
                    # print(result)
                    if result[2] != 'A':
                        mqt_pub.publish(str(str(result[0]) + str(result[1])), result[3])
                        print("redo publish")
                        print(str(str(result[0]) + str(result[1])) + ", " + result[3])
                # 站點與倉庫的TABLE不同所以要分開select
                sql = "SELECT w.station_id,w.ack_handshaking,w.cmd_id,w.timestamp_id FROM YID.warehouse_error w where w.warehouse_error_id " \
                      "in (SELECT max(w.warehouse_error_id) FROM YID.warehouse_error w where w.cmd_id=5);"
                mycursor.execute(sql)
                result = mycursor.fetchone()
                # print(result)
                if result[1] != 'A':
                    mqt_pub.publish("75", result[3])
                    print("redo publish")
                    print("75, " + result[3])
                print("check db")
                mydb.close()
                mycursor.close()
            except Exception as e:
                print("check db error:", e)
                # trace.back()

            threading.Event().wait(1)

    def startpingthread(self):
        print('ping')
        pingthread = threading.Thread(target=self.play_ping)
        pingthread.start()

    def play_ping(self):
        while True:
            threading.Event().wait(2)
            try:
                response = os.system("ping -c 1 " + self.address)
                if response == 0:
                    self.iLink = 1
                    self.btn_linkage_str.set("連線")
                    self.btn_linkage.configure(image=self.img1)
                    self.btn_linkage.image = self.img1
                    self.btn_linkage.configure(fg="white")
                else :
                    self.iLink = 0
                    self.btn_linkage_str.set("離線")
                    self.btn_linkage.configure(image=self.img4)
                    self.btn_linkage.image = self.img4
                    self.btn_linkage.configure(fg="white")
            except Exception as e:
                print("PING error:", e)

            threading.Event().wait(8)

    def startmp3thread(self):
        print('play mp3')
        mp3thread = threading.Thread(target=self.play_mp3)
        mp3thread.start()

    def play_mp3(self):
        while True:
            while (self.error_station != 0) & (self.music_loop < 10):
                mixer.init()
                if int(self.error_station) == 1:
                    mixer.music.load(Config.music_1)
                elif int(self.error_station) == 2:
                    mixer.music.load(Config.music_2)
                elif int(self.error_station) == 3:
                    mixer.music.load(Config.music_3)
                elif int(self.error_station) == 4:
                    mixer.music.load(Config.music_4)
                elif int(self.error_station) == 5:
                    mixer.music.load(Config.music_5)
                elif int(self.error_station) == 6:
                    mixer.music.load(Config.music_6)
                elif int(self.error_station) == 7:
                    mixer.music.load(Config.music_7)
                mixer.music.play()
                print('music begin')
                while mixer.music.get_busy():  # wait for music to finish playing
                    time.sleep(1)
                print('music end')
                self.music_loop += 1

            threading.Event().wait(1)
    def uptitlethread(self):
        print('ping')
        uptitlethread = threading.Thread(target=self.uptitle)
        uptitlethread.start()
    def uptitle(self):
        while True:
            cpu = CPUTemperature()
            root.title('YID ' + get_ip_address() + ", "+ datetime.now().strftime('%Y%m%d%H%M%S') + ", " + str(cpu).split("=")[1].replace(">","") + "C, " + str(threading.active_count()) + ", " + getCPUuse()+"%")
            threading.Event().wait(1)
    def shutdownConfirm(self):
        # 關機確認視窗
        r = tk.messagebox.askyesno('對話框', '確定要重新開機嗎？')
        if r == True:
            # print("shutdown!")
            # os.system("sudo shutdown -h now")
            print("reboot!")
            os.system("sudo reboot")
if __name__ == '__main__':
    time.sleep(1)
    root = tk.Tk()
    app = App(root)
    root.mainloop()

