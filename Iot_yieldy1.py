#!/usr/bin/python
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time
import pigpio
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import simplejson as json
import math
import threading

# Called when connect to Broker
def on_VLCConnect(client, userdata, flags, rc):
  print("Connected with result code " +str(rc))
  client.subscribe("yieldy1/adjust_brightness", qos=2)
  client.subscribe("yieldy2/adjust_brightness", qos=2)
  client.subscribe("yieldy3/adjust_brightness", qos=2)
  client.subscribe("manufacture/main", qos=2)
  client.subscribe("delivery_place/delivery", qos=2)
  client.subscribe("retailer/sell", qos=2)
  client.subscribe("buyer/buy", qos=2)

# Called when publish
def on_VLCPublish(client, userdata, mid):
  print("OK2")

lock_start=0
determine_data_group=0
#tea1
# asset_RFID_array=['tea1']
# asset_ldr_RFID_array=['Z001']
# leave_stage_time=5

#Desiccant1
# asset_RFID_array=['Desiccant1']
# asset_ldr_RFID_array=['Z002']
# leave_stage_time=5

#wrapper1
# asset_RFID_array=['wrapper1']
# asset_ldr_RFID_array=['Z003']
# leave_stage_time=5

#tea1
# asset_RFID_array=['tea1']
# asset_ldr_RFID_array=['Z001']
# leave_stage_time=15

#tea1
# asset_RFID_array=['tea1']
# asset_ldr_RFID_array=['Z001']
# leave_stage_time=5

#tea1
# asset_RFID_array=['tea1']
# asset_ldr_RFID_array=['Z001']
# leave_stage_time=5

#tea1
asset_RFID_array=['tea1']
asset_ldr_RFID_array=['Z001']
leave_stage_time=5

def on_recevice(client, userdata, msg):
  global lock_start
  global asset_RFID_array,asset_ldr_RFID_array
  if(msg.topic == "yieldy1/adjust_brightness"):
    print('start yieldy1/adjust_brightness')
    lock_start = 1

  if(msg.topic == "yieldy2/adjust_brightness"):
    print('start yieldy2/adjust_brightness')
    lock_start = 1

  if(msg.topic == "yieldy3/adjust_brightness"):
    print('start yieldy3/adjust_brightness')
    lock_start = 1

  if(msg.topic == "manufacture/main"):
    print('start manufacture/main')
    lock_start = 1

  if(msg.topic == "delivery_place/delivery"):
    print('start delivery_place/delivery')
    lock_start = 1

  if(msg.topic == "retailer/sell"):
    print('start retailer/sell')
    lock_start = 1

  if(msg.topic == "buyer/buy"):
    print('start buyer/buy')
    lock_start = 1



#client = mqtt.Client("", True, None, mqtt.MQTTv31)
client = mqtt.Client()
client.on_connect = on_VLCConnect
client.on_publish = on_VLCPublish
client.on_message = on_recevice
#client.connect("mqtt.eclipse.org", 1883, 60)
#client.connect("iot.eclipse.org", 1883, 60)
# client.username_pw_set('aucsie01','1234')
# client.connect_async("192.168.0.231", 1883, 60)
client.username_pw_set('aucsie07','1234')
client.connect_async("192.168.1.133", 1883, 60)
client.loop_start()
#client.connect("192.168.0.231", 8883, 60)

start = time.time()
stage_task=[
    'adjust_brightness',
]

mqtt_service_channel=[
  "sensor_login",
  "sensor_data",
  "sensor_logout",
]

client.publish((mqtt_service_channel[0]), json.dumps({'determine_data_group':determine_data_group,'asset_RFID':asset_RFID_array[determine_data_group],'asset_sensor_RFID':asset_ldr_RFID_array[determine_data_group],'start_time':start,'sensor_type':'ldr'}), qos=2)
init_determine_second = 5

SPI_PORT   = 0
SPI_DEVICE = 0
SIGNAL_CHANNEL = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
pi = pigpio.pi()

IDR_data_array = []
switch_value=0
count_send_data_packet=0
determine_sensor_start=0

recode_IDR_data_array_content_avg_array=[]
recode_IDR_data_array_content_item_array=[]

def ldr_run():
  global lock_start,start,determine_sensor_start,init_determine_second,leave_stage_time
  global switch_value,IDR_data_array
  global count_send_data_packet,determine_data_group
  global asset_RFID_array,asset_ldr_RFID_array
  global client,sent_json,mqtt_service_channel
  global recode_IDR_data_array_content_avg_array,recode_IDR_data_array_content_item_array
  
  try:
    while True:
      if(lock_start == 1):
        start = time.time()
        lock_start = 0
        determine_sensor_start = 1

      if(determine_sensor_start == 1):
        end = time.time()
        end_cut_start_sed = int(math.floor(end-start))
        if math.floor((end_cut_start_sed/60)) < leave_stage_time:
          #print("test_second:"+str(round((end_cut_start_sed/60))))
          switch_value = mcp.read_adc(SIGNAL_CHANNEL)
          # if(len(IDR_data_array) < 5):
          #   IDR_data_array.append(switch_value)
          IDR_data_array.append(switch_value)
          if(int(end_cut_start_sed%5) == 0) and (end_cut_start_sed == init_determine_second):
            init_determine_second+=5
            count_send_data_packet+=1
            print('count_send_data_packet:'+str(count_send_data_packet))

            count_IDR_data_array_content=0
            for IDR_data_array_item in IDR_data_array:
              count_IDR_data_array_content = count_IDR_data_array_content+len(str(IDR_data_array_item))+1
            recode_IDR_data_array_content_avg_array.append(int((count_IDR_data_array_content-1)))

            sent_json = json.dumps({'determine_data_group':determine_data_group,'asset_RFID':asset_RFID_array[determine_data_group],'asset_sensor_RFID':asset_ldr_RFID_array[determine_data_group],'sensor_value':IDR_data_array,'packet_number':count_send_data_packet,'sensor_type':'ldr'})
            client.publish((mqtt_service_channel[1]),sent_json, qos=2)
            IDR_data_array = []
        if math.floor((end_cut_start_sed/60)) == leave_stage_time:
          count_send_data_packet+=1
          print('count_send_data_packet:'+str(count_send_data_packet))

          count_IDR_data_array_content=0
          for IDR_data_array_item in IDR_data_array:
            count_IDR_data_array_content = count_IDR_data_array_content+len(str(IDR_data_array_item))+1
          recode_IDR_data_array_content_avg_array.append(int((count_IDR_data_array_content-1)))

          count_recode_IDR_data_array_content_avg_array_item=0
          print(recode_IDR_data_array_content_avg_array)
          for recode_IDR_data_array_content_avg_array_item in recode_IDR_data_array_content_avg_array:
            count_recode_IDR_data_array_content_avg_array_item = count_recode_IDR_data_array_content_avg_array_item+recode_IDR_data_array_content_avg_array_item
          print(count_recode_IDR_data_array_content_avg_array_item)
          print('recode_IDR_data_array_content_avg:'+str(int(count_recode_IDR_data_array_content_avg_array_item/len(recode_IDR_data_array_content_avg_array))))

          sent_json = json.dumps({'determine_data_group':determine_data_group,'asset_RFID':asset_RFID_array[determine_data_group],'asset_sensor_RFID':asset_ldr_RFID_array[determine_data_group],'sensor_value':IDR_data_array,'packet_number':count_send_data_packet,'sensor_type':'ldr'})
          client.publish((mqtt_service_channel[1]),sent_json, qos=2)
          print((mqtt_service_channel[2]))
          client.publish((mqtt_service_channel[2]), json.dumps({'determine_data_group':determine_data_group,'asset_RFID':asset_RFID_array[determine_data_group],'asset_sensor_RFID':asset_ldr_RFID_array[determine_data_group],'sensor_type':'ldr'}), qos=2)
          time.sleep(30)
          client.loop_stop()
          client.loop_start()
          IDR_data_array = []
          init_determine_second = 0
          print('ldr_logout:')
          determine_sensor_start=0
          #break
  except KeyboardInterrupt:
    print("test")


ldr_run_Thread = threading.Thread(target = ldr_run)
ldr_run_Thread.start()