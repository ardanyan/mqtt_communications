#!/usr/bin/env python3

from serial import Serial
import time
ser = Serial('/dev/ttyUSB0', 9600, timeout=1)

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

        print(dataDict)
    time.sleep(3)
ser.close()
