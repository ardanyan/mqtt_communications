import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, message):
    print("received message: " , json.loads(message.payload.decode('utf-8')))

broker = "localhost"


client = mqtt.Client("sensor_listener")
client.connect(broker)

client.loop_start()
client.subscribe("sensor_data")
client.on_message=on_message

while True:
    pass
