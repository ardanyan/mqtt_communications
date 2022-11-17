import paho.mqtt.client as mqtt
import json
from datetime import datetime

HOST = "93ac6c9412324249b4ef263401803a6e.s1.eu.hivemq.cloud" # Host Raspberry IP Address
TOPIC = "sensor_data"
FORMAT = "utf-8"


def logger_callback(msg) -> None:
    print("[SUBSCRIBER] {} - {}".format(
        datetime.now().strftime("%y/%m/%d %H:%M:%S.%f"), msg))

def on_message_callback(client, userdata, message):
    logger_callback("Received message: {}".format(
        json.loads(message.payload.decode(FORMAT))))


class Subscriber:
    def __init__(self, client_id:str) -> None:
        self.__client = mqtt.Client(client_id)
        self.__logger = logger_callback
        self.__client.on_connect = None
        self.__client.on_message = on_message_callback
        
    def start(self, host:str=HOST) -> None:
        self.__client.connect(host)
        self.__logger("Started")
    
    def subscribe(self, topic:str) -> None:
        self.__client.loop_start() # Activates callbacks
        self.__client.subscribe(topic)
        self.__logger("Subscribed to the topic \'{}\'".format(topic))
        
    def close(self) -> None:
        self.__client.loop_stop() # Deactivate callbacks
        self.__client.disconnect()
        self.__logger("Disconnected")


if __name__ == "__main__":
    subscriber_client = Subscriber("SWAIN_Subscriber")
    subscriber_client.start() # Default parameters
    subscriber_client.subscribe(TOPIC)
    while True:
        try: continue
        except KeyboardInterrupt:
            subscriber_client.close()
            break
    exit()
