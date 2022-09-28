User = "rastreamento@ttn"
Password = "NNSXS.TT6B7SGAZXGUDMX37KEDERCVALKOMET43JDNYQI.2BV5DVLUDWUVXLULJ43SVJOB636LZZ3RP5IIDSSBAP5SAZZ5JZVQ"
User_password = "NNSXS.FD3O3OMZKXFE6KVDS3RNRNZUT47L4MVYLC7REBI.OJJRJQ5GIR2B4A22XYPRLDI64PXQOIEBXVMZD52VKZIIEBEIWADA"
Organization_password = "NNSXS.QEKN262SW4UOZ3OBQLKPUZDJPOY7OVGTL5RHRDQ.BEDDSFM5IOOP4EDUGVUBX63DQZQ6J77HK2RJHI243XXMXKJSVI2A"
Organization_id = "utfpr-td-lora"
theRegion = "AU1"		# The region you are using

# URL e header para requisição HTTP da organização na TTN
ttn_url = "https://eu1.cloud.thethings.network/api/v3/organizations/utfpr-td-lora/applications"
header_ttn = {
	"Authorization": "Bearer NNSXS.QEKN262SW4UOZ3OBQLKPUZDJPOY7OVGTL5RHRDQ.BEDDSFM5IOOP4EDUGVUBX63DQZQ6J77HK2RJHI243XXMXKJSVI2A"
}

VER  = "16-03-2022 v1.0"
import os, sys, logging, time
from urllib import request
print(os.path.basename(__file__) + " " + VER)

print("Imports:")
import paho.mqtt.client as mqtt
import json
import csv
from datetime import datetime
import requests
from sentilo_parser import parser

print("Functions:")

# Write uplink to tab file
def saveToFile(someJSON):
	end_device_ids = someJSON["end_device_ids"]
	device_id = end_device_ids["device_id"]
	application_id = end_device_ids["application_ids"]["application_id"]
	
	received_at = someJSON["received_at"]
	
	uplink_message = someJSON["uplink_message"];
	f_port = uplink_message["f_port"];
	f_cnt = uplink_message["f_cnt"];
	frm_payload = uplink_message["frm_payload"];
	rssi = uplink_message["rx_metadata"][0]["rssi"];
	snr = uplink_message["rx_metadata"][0]["snr"];
	# data_rate_index = uplink_message["settings"]["data_rate_index"];
	consumed_airtime = uplink_message["consumed_airtime"];
	lat = uplink_message["decoded_payload"]["latitude"]
	lng = uplink_message["decoded_payload"]["longitude"]
	
	# Daily log of uplinks
	now = datetime.now()
	pathNFile = now.strftime("%Y%m%d") + ".txt"
	print(pathNFile)
	if (not os.path.isfile(pathNFile)):
		with open(pathNFile, 'a', newline='') as tabFile:
			fw = csv.writer(tabFile, dialect='excel-tab')
			fw.writerow(["received_at", "application_id", "device_id", "f_port", "f_cnt", "frm_payload", "rssi", "snr", "consumed_airtime", "latitude", "longitude"])
	
	with open(pathNFile, 'a', newline='') as tabFile:
		fw = csv.writer(tabFile, dialect='excel-tab')
		fw.writerow([received_at, application_id, device_id, f_port, f_cnt, frm_payload, rssi, snr, consumed_airtime, lat, lng])

	# Application log
	pathNFile = application_id + ".txt"
	print(pathNFile)
	if (not os.path.isfile(pathNFile)):
		with open(pathNFile, 'a', newline='') as tabFile:
			fw = csv.writer(tabFile, dialect='excel-tab')
			fw.writerow(["received_at", "device_id", "f_port", "f_cnt", "frm_payload", "rssi", "snr", "consumed_airtime", "latitude", "longitude"])
	
	with open(pathNFile, 'a', newline='') as tabFile:
		fw = csv.writer(tabFile, dialect='excel-tab')
		fw.writerow([received_at, device_id, f_port, f_cnt, frm_payload, rssi, snr, consumed_airtime, lat, lng])
	
	# Device log
	pathNFile = application_id + "__" + device_id + ".txt"
	print(pathNFile)
	if (not os.path.isfile(pathNFile)):
		with open(pathNFile, 'a', newline='') as tabFile:
			fw = csv.writer(tabFile, dialect='excel-tab')
			fw.writerow(["received_at", "f_port", "f_cnt", "frm_payload", "rssi", "snr", "consumed_airtime", "latitude", "longitude"])
	
	with open(pathNFile, 'a', newline='') as tabFile:
		fw = csv.writer(tabFile, dialect='excel-tab')
		fw.writerow([received_at, f_port, f_cnt, frm_payload, rssi, snr, consumed_airtime, lat, lng])

	# redirect(lat, lng)

# MQTT event functions
def on_connect(mqttc, obj, flags, rc):
	if rc == 0:
		print("Connection successful!")
	elif rc == 1:
		print("Connection refused – invalid client identifier")
	elif rc == 2:
		print("Connection refused – invalid client identifier")
	elif rc == 3:
		print("Connection refused – server unavailable")
	elif rc == 4:
		print("Connection refused – bad username or password")
	elif rc == 5:
		print("Connection refused – not authorised")

	print("\nReturn code: " + str(rc))

def on_message(mqttc, obj, msg):
	print("\nMessage: " + msg.topic + " " + str(msg.qos)) # + " " + str(msg.payload))
	parsedJSON = json.loads(msg.payload)
	try:
		parser(parsedJSON)
	except:
		print("Error while parsing to Sentilo")
    # saveToFile(parsedJSON)

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("\nSubscribe: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc, obj, level, string):
    print("\nLog: "+ string)
    logging_level = mqtt.LOGGING_LEVEL[level]
    logging.log(logging_level, string)

# Atualiza a lista de aplicações que a organização colabora
def get_apps(app_ids, clients):
	resp = requests.get(ttn_url, headers=header_ttn)
	parsedResp = json.loads(resp.text)["applications"]
	for item in parsedResp:
		new_app = item["ids"].get("application_id")
		print("app_id %s" % new_app)
		if new_app not in app_ids:
			app_ids.append(new_app)
			# connects new app to a new MQTT client
	return

# Handling multiple clients - TODO
# app_ids = [] # Lista de aplicações que a organização é colaboradora
# clients = [] # Lista de clientes MQTT
# get_apps(app_ids, clients)

# Init mqtt client
mqttc = mqtt.Client()

# Assign callbacks
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_message = on_message

print("Connect")
# Setup authentication from settings above
mqttc.username_pw_set(User, Organization_password)
mqttc.connect("au1.cloud.thethings.network", 1883, 60)
# Subscribe to
mqttc.subscribe("v3/+/devices/+/up", 0)	# all device uplinks

print("And run forever")
try:
	mqttc.loop_forever(10) # 10 segundos de delay
except KeyboardInterrupt:
	mqttc.disconnect()
	print("Exit")
	sys.exit(0)
except:
	print("Something went wrong!")
	mqttc.disconnect()
	sys.exit(0)