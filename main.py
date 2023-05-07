import Adafruit_DHT
import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.client as paho
from paho import mqtt

GPIO.setmode(GPIO.BCM)

# Set the GPIO pin number for the DHT11 sensor
DHT_PIN = 2# Define the pin number to use
servo_pin = 17

# Set the pin as an output
GPIO.setup(servo_pin, GPIO.OUT)

# Create a PWM object with a frequency of 50Hz
pwm = GPIO.PWM(servo_pin, 50)


# Define the duty cycle for each angle (from 0 to 180 degrees)
angle_0 = 3.5  # Duty cycle for 0 degrees
angle_45 = 6.5  # Duty cycle for 45 degrees
angle_90 = 9.5  # Duty cycle for 90 degrees
angle_180 = 12.5  # Duty cycle for 180 degrees

pwm.start(angle_0)

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client
client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect

# enable TLS for secure connection
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
client.username_pw_set("harindu", "harindu123")
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client.connect("4a799902a63b49f4a4bf1257f9b18639.s2.eu.hivemq.cloud", 8883)

# setting callbacks, use separate functions like above for better visibility
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish

while True:
	# Read temperature and humidity from the DHT11 sensor
	humidity, temperature_c = Adafruit_DHT.read_retry(11, DHT_PIN)

	# Convert temperature to Fahrenheit
	temperature_f = temperature_c * 9/5.0 + 32

	# Calculate the heat index using the formula provided by the National Weather Service
	heat_index_f = (-42.379 + (2.04901523 * temperature_f) + (10.14333127 * humidity) - (0.22475541 * temperature_f * humidity) - (0.00683783 * temperature_f**2) - (0.05481717 * humidity**2) + (0.00122874 * temperature_f**2 * humidity) + (0.00085282 * temperature_f * humidity**2) - (0.00000199 * temperature_f**2 * humidity**2))

	# Print the temperature, humidity, and heat index in Fahrenheit
	print("Temperature: {:.1f}°C".format(temperature_c))
	print("Humidity: {:.1f}%".format(humidity))
	print("Heat index: {:.1f}°F".format(heat_index_f))
	
	# a single publish, this can also be done in loops, etc.
	client.publish("iot/temperature", payload=temperature_c, qos=0)
	client.publish("iot/humidity", payload=humidity, qos=0)
	client.publish("iot/heatIndex", payload=round(heat_index_f,2), qos=0)
	
	#Rotate servo
	if heat_index_f < 80.00:
		pwm.ChangeDutyCycle(angle_180)
	elif heat_index_f >= 80.00 and heat_index_f < 90.00:
		pwm.ChangeDutyCycle(angle_180)
	elif heat_index_f >= 90.00 and heat_index_f < 103.00:
		pwm.ChangeDutyCycle(angle_45)
	elif heat_index_f >= 103.00 and heat_index_f < 124.00:
		pwm.ChangeDutyCycle(angle_90)
	else:
		pwm.ChangeDutyCycle(angle_0)
		
	sleep(5)
