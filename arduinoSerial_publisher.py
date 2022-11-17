#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import socket
from serial import Serial
import json

ser = Serial('/dev/ttyUSB0', 9600, timeout=1)

#broker = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
broker = "192.168.43.114" #Host raspberry ip address
client = mqtt.Client("swain_publisher")#, True, None, mqtt.MQTTv31)
client.connect(broker)

dataDict = dict()

while True:
    #print(ser.readline())
    msg = ser.readline()
    dataList = msg.split(b"$")
    if(len(dataList) > 1):
        #print(data)
        for data in dataList:
            if not data == b'\r\n':
                data = str(data.decode('utf-8'))
                #print(data)
                #print("*************")
                splitted = data.split(":")
                dataDict[splitted[0]] = splitted[1]

        print("dict::::")
        print(dataDict)
        databytes = json.dumps(dataDict).encode('utf-8')
        client.publish("sensor_data", databytes)

ser.close()
