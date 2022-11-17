#!/usr/bin/env python3
from serial import Serial
import json

import paho.mqtt.client as mqtt
import socket

from datetime import datetime
from pytz import timezone
import time


# Serial Settings
SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
SERIAL_TIMEOUT = 1

# Broker Settings
HOST = "broker.hivemq.com" # Host Raspberry IP Address
TOPIC = "sensor_data"

# Other
FORMAT = "utf-8"
SEPERATOR = b"$"
KEY_VALUE_SEPERATOR = ":"
LINE_END = b"\r\n"
SLEEP_TIMEOUT = 1 # in seconds

def get_timestamp() -> str:
    return datetime.now(timezone("UTC")).strftime("%y/%m/%d %H:%M:%S.%f %Z%z")

def get_file_name() -> str:
    return datetime.now(timezone("UTC")).strftime("%y-%m-%d") + ".txt"

def logger_callback(msg:str) -> None:
    print("[PUBLISHER] {} - {}".format(
        get_timestamp(), msg))

def on_publish_callback(client, userdata, message):
    pass


class Publisher:
    def __init__(self, client_id:str) -> None:
        self.__serial = Serial(SERIAL_PORT, BAUDRATE, timeout=SERIAL_TIMEOUT)
        self.__client = mqtt.Client(client_id)
        self.__logger = logger_callback
        self.__client.on_connect = None
        self.__client.on_publish = on_publish_callback
        
    def __read(self) -> dict:
        data_as_dict = dict()
        msg = self.__serial.readline()
        data_as_list = msg.split(SEPERATOR)
        
        if(len(data_as_list) > 1):
            data_as_dict.update(
                {"timestamp": get_timestamp()})
            
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
        
    def record_locally(self) -> None:
        while True:
            try:
                data_as_dict = self.__read()
                if data_as_dict is not None:
                    with open(get_file_name(), "a+") as file:
                        json.dump(data_as_dict, file)
                        file.write("\n")
                        self.__logger("Written into local file")
                time.sleep(SLEEP_TIMEOUT)
            except UnicodeDecodeError:
                self.__serial.close()
                time.sleep(SLEEP_TIMEOUT)
                self.__serial = Serial(SERIAL_PORT, BAUDRATE, timeout=SERIAL_TIMEOUT)
        

if __name__ == "__main__":
    time.sleep(3)
    publisher_client = Publisher("SWAIN_Publisher")
    """publisher_client.start() # Default parameters
    while True:
        try:
            publisher_client.publish(TOPIC)
        except KeyboardInterrupt:
            publisher_client.close()
            break
    exit()"""
    publisher_client.record_locally()