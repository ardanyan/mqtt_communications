#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import socket
from serial import Serial
import json
from datetime import datetime
import time

"""ser = Serial('/dev/ttyUSB0', 9600, timeout=1)

broker = "10.42.0.1"
client = mqtt.Client("sensor_publisher")#, True, None, mqtt.MQTTv31)
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

ser.close()"""

# Serial Settings
SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
TIMEOUT = 1

# Broker Settings
HOST = "192.168.43.114" # Host Raspberry IP Address
TOPIC = "sensor_data"

# Other
FORMAT = "utf-8"
SEPERATOR = b"$"
KEY_VALUE_SEPERATOR = ":"
LINE_END = b"\r\n"


def logger_callback(msg:str) -> None:
    print("[PUBLISHER] {} - {}".format(
        datetime.now().strftime("%y/%m/%d %H:%M:%S.%f"), msg))

def on_publish_callback(client, userdata, message):
    pass


class Publisher:
    def __init__(self, client_id:str) -> None:
        self.__serial = Serial(SERIAL_PORT, BAUDRATE, timeout=TIMEOUT)
        self.__client = mqtt.Client(client_id)
        self.__logger = logger_callback
        self.__client.on_connect = None
        self.__client.on_publish = on_publish_callback
        
    def __read(self) -> dict:
        data_as_dict = dict()
        msg = self.__serial.readline()
        data_as_list = msg.split(SEPERATOR)
        
        if(len(data_as_list) > 1):
            for each in data_as_list:
                if not each == LINE_END:
                    each = str(each.decode(FORMAT))
                    splitted = each.split(KEY_VALUE_SEPERATOR)
                    data_as_dict[splitted[0]] = splitted[1]
        
            return data_as_dict
        return None
        
    def start(self, host:str=HOST) -> None:
        self.__client.connect(host)
        self.__client.loop_start() # Activates callbacks
        self.__logger("Started")
        
    def publish(self, topic:str) -> None:
        data_as_dict = self.__read()
        if data_as_dict is not None:
            data_as_bytes = json.dumps(data_as_dict).encode(FORMAT)
            self.__client.publish(topic, data_as_bytes)
            self.__logger("Published to the topic \'{}\'".format(topic))
        
    def close(self) -> None:
        self.__serial.close()
        self.__client.loop_stop() # Deactivates callbacks
        self.__client.disconnect()
        self.__logger("Disconnected")

if __name__ == "__main__":
    publisher_client = Publisher("SWAIN_Publisher")
    publisher_client.start() # Default parameters
    while True:
        try:
            publisher_client.publish(TOPIC)
        except KeyboardInterrupt:
            publisher_client.close()
            break
    exit()