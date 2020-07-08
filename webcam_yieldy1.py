import paho.mqtt.client as mqtt
import cv2
import time
import hashlib
import os
import sys
import simplejson as json
import math
from darkflow.net.build import TFNet
import threading
from paramiko import SSHClient
from scp import SCPClient

option = {'model': './darkflow/cfg/yolo-tiny.cfg', 
	        'load': './darkflow/bin/yolo-tiny.weights',
	        'config':'./darkflow/cfg/',
          'thereshold': 0.1}
#./darkflow/cfg/tiny-yolo.cfg
#可配
 #./
#不可配
 #./tiny-yolo.weights(不匹配)
 #./tiny-yolo.v1.1.weights(不匹配)
 #./yolo-tiny.weights(數值會亂跳)

#./darkflow/cfg/yolo.cfg
#可配
 #./yolov3.weights
#不可配
tfnet = TFNet(option)

#set camera
cap = cv2.VideoCapture(0)
# 設定擷取影像的尺寸大小
#320 C270 720P max 1280
frame_width=320
#240 C270 720P max 240
frame_hight=240
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_hight)

# 使用FFV1編碼
#fourcc = cv2.VideoWriter_fourcc(*'XVID')
#fourcc = cv2.VideoWriter_fourcc(*'X264')
fourcc = cv2.VideoWriter_fourcc(*'FFV1')

# 建立 VideoWriter 物件，輸出影片至 output.avi
# FPS 值為 20.0，解析度為 640x360
#turne fps
fps = 1
frame_size_tuple=(frame_width, frame_hight)

# local_path = './video_org/yieldy1_adjust_brightness.avi'
# remote_path = '/home/aucsie07/aucsie01_backup/webcam/video_org/yieldy1_adjust_brightness.avi'

# local_path = './video_org/yieldy2_adjust_brightness.avi'
# remote_path = '/home/aucsie07/aucsie01_backup/webcam/video_org/yieldy2_adjust_brightness.avi'

# local_path = './video_org/yieldy3_adjust_brightness.avi'
# remote_path = '/home/aucsie07/aucsie01_backup/webcam/video_org/yieldy3_adjust_brightness.avi'

# local_path = './video_org/manufacture_main.avi'
# remote_path = '/home/aucsie07/aucsie01_backup/webcam/video_org/manufacture_main.avi'

# local_path = './video_org/delivery_place_delivery.avi'
# remote_path = '/home/aucsie07/aucsie01_backup/webcam/video_org/delivery_place_delivery.avi'

# local_path = './video_org/retailer_sell.avi'
# remote_path = '/home/aucsie07/aucsie01_backup/webcam/video_org/retailer_sell.avi'

local_path = './video_org/buyer_buy.avi'
remote_path = '/home/aucsie07/aucsie01_backup/webcam/video_org/buyer_buy.avi'

out = cv2.VideoWriter(local_path, fourcc, fps, frame_size_tuple)
#mp4 cannot work
# out = cv2.VideoWriter('./video_org/output_yieldy1.mp4', fourcc, 1, (640, 360))


ssh = SSHClient()
ssh.load_system_host_keys()
ssh.connect('192.168.1.133',22,'aucsie07','1234')
scp = SCPClient(ssh.get_transport())

stage_task=[
    'adjust_brightness',
]

mqtt_service_channel=[
  "sensor_login",
  "sensor_data",
  "sensor_logout",
]

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
  print("OK")

lock_start=0
determine_sensor_start=0
determine_data_group=0

#yieldy1 tea1
# asset_RFID_array=['tea1']
# asset_camera_RFID_array=['C001']
# leave_stage_time=5

#yieldy2 Desiccant1
# asset_RFID_array=['Desiccant1']
# asset_camera_RFID_array=['C002']
# leave_stage_time=5

#yieldy3 wrapper1
# asset_RFID_array=['wrapper1']
# asset_camera_RFID_array=['C003']
# leave_stage_time=5

#manufacture tea1
# asset_RFID_array=['tea1']
# asset_camera_RFID_array=['C001']
# leave_stage_time=15

#delivery_place tea1
# asset_RFID_array=['tea1']
# asset_camera_RFID_array=['C001']
# leave_stage_time=5

#retailer tea1
# asset_RFID_array=['tea1']
# asset_camera_RFID_array=['C001']
# leave_stage_time=5

#buyer tea1
asset_RFID_array=['tea1']
asset_camera_RFID_array=['C001']
leave_stage_time=5

def on_recevice(client, userdata, msg):
  global lock_start
  global asset_RFID_array,asset_camera_RFID_array

  print(msg.topic)
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

# def on_BrokerMessage(client, userdata, mid):
  # if(msg.topic == (mqtt_service_channel[0])):
  #   print(msg.topic)
  # if(msg.topic == (mqtt_service_channel[1])):
  #   print(msg.topic)
  # if(msg.topic == (mqtt_service_channel[2])):
  #   print(msg.topic)

yolo_tag_array = []
frame_hash_array = []

client = mqtt.Client()
client.on_connect = on_VLCConnect
client.on_publish = on_VLCPublish
client.on_message = on_recevice
# client.username_pw_set('aucsie01','1234')
# client.connect_async("192.168.0.231", 1883, 60)
#client.username_pw_set('aucsie07','1234')
client.connect_async("192.168.1.133", 1883, 60)
client.loop_start()
start = time.time()
client.publish((mqtt_service_channel[0]), json.dumps({'determine_data_group':determine_data_group,'asset_RFID':asset_RFID_array[determine_data_group],'asset_sensor_RFID':asset_camera_RFID_array[determine_data_group],'video_path':local_path,'start_time':start,'sensor_type':'camera'}), qos=2)

# test_frame_submit
# frame_submit = 0

# if(os.path.isfile("hash_recode.txt")):
#   os.remove("hash_recode.txt")
# hash_recode = open("hash_recode.txt", "w+")

# set n second
init_determine_n_second = 5
count_send_data_packet=0

count_yolo_tag_string_len_avg_array = []
count_frame_hash_array_len_avg_array = []

def camera_run():
  global lock_start,determine_sensor_start,init_determine_n_second,leave_stage_time
  global fps,cv2,out,cap,frame_width,frame_hight,fourcc,frame_size_tuple
  global frame_hash_array,yolo_tag_array,count_send_data_packet
  global determine_data_group,mqtt_service_channel
  global asset_RFID_array,asset_camera_RFID_array
  global client,sent_json
  global count_yolo_tag_string_len_avg_array,count_frame_hash_array_len_avg_array

  while(True):
    if(lock_start == 1):
      start = time.time()
      lock_start = 0
      determine_sensor_start = 1

    if(determine_sensor_start == 1):
      cv2.waitKey(fps)
      ret, frame = cap.read()
      end = time.time()
      end_cut_start_sed = int(math.floor(end-start))
      if (math.floor((end_cut_start_sed/60)) < leave_stage_time):
          if ret == True:
            # 寫入影格
            #delay, the parameter is fps and int type
            out.write(frame)
            print('int(end-start):'+str(end_cut_start_sed))
            # show view in screen
            #cv2.imshow('frame',frame)
            #does not use BIS
            hash_frame = str(frame.tobytes())
            print("hash_frame_lenght:"+str(len(hash_frame)))
            #use BIS
            #hash_frame = hashlib.sha256(frame.tobytes()).hexdigest()
            # hash_recode.write(hash_frame+"\n")
            frame_hash_array.append(hash_frame)
            print('int(end-start)----------------------------------------------------'+str(end_cut_start_sed))
            results = tfnet.return_predict(frame)
            #colculater fps
            #yolo data
            #print(results)
            for result in results:
              yolo_tag_array.append(result['label'])
              tl = (result['topleft']['x'], result['topleft']['y'])
              br = (result['bottomright']['x'], result['bottomright']['y'])
              cv2.rectangle(frame, tl, br, (0, 255, 0), 7, )
              cv2.putText(frame, result['label'], tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
            #count n second rusult(n=5) and first time not recode
            if (int(end_cut_start_sed%5) == 0) and (end_cut_start_sed == init_determine_n_second):
              init_determine_n_second+=5
              #n second sent data
              #print('frame_hash_array:'+str(frame_hash_array))
              yolo_tag_array = {}.fromkeys(yolo_tag_array).keys()
              count_send_data_packet+=1

              count_yolo_tag_string_len = 0
              count_yolo_total_tag_in_array=0
              for count_yolo_tag_array in yolo_tag_array:
                #+1 use to ,
                count_yolo_tag_string_len = count_yolo_tag_string_len+len(count_yolo_tag_array)+1
                count_yolo_total_tag_in_array+=1
              count_yolo_tag_string_len_avg_array.append(int((count_yolo_tag_string_len-1)))

              count_frame_hash_string_len = 0
              for count_frame_hash_array_item in frame_hash_array:
                count_frame_hash_string_len = count_frame_hash_string_len+len(count_frame_hash_array_item)+1
              count_frame_hash_array_len_avg_array.append(int((count_frame_hash_string_len-1)))

              print('count_send_data_packet:'+str(count_send_data_packet))
              sent_json = json.dumps({'determine_data_group':determine_data_group,'asset_RFID':asset_RFID_array[determine_data_group],'asset_sensor_RFID':asset_camera_RFID_array[determine_data_group],'frame_hash_array':tuple(frame_hash_array),'yolo_tag_array':tuple(yolo_tag_array),'packet_number':count_send_data_packet,'sensor_type':'camera'})
              #print(sent_json)
              client.publish((mqtt_service_channel[1]), sent_json, qos=2)
              # frame_submit+=1
              # print('frame_submit***********************************************'+str(frame_submit))
              #print('yolo_tag_array:'+str(yolo_tag_array))
              #clean frame_hash_array 
              #tuple translate to list
              yolo_tag_array = list(yolo_tag_array)
              yolo_tag_array = []
              frame_hash_array = list(frame_hash_array)
              frame_hash_array = []
            #leave scenes min
      elif math.floor((end_cut_start_sed/60)) == leave_stage_time:
        # 釋放所有資源
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        yolo_tag_array = {}.fromkeys(yolo_tag_array).keys()
        count_send_data_packet+=1

        count_yolo_tag_string_len = 0
        count_yolo_total_tag_in_array=0
        for count_yolo_tag_array in yolo_tag_array:
          count_yolo_tag_string_len = count_yolo_tag_string_len+len(count_yolo_tag_array)+1
          count_yolo_total_tag_in_array+=1
        count_yolo_tag_string_len_avg_array.append(int((count_yolo_tag_string_len-1)))

        count_frame_hash_string_len = 0
        for count_frame_hash_array_item in frame_hash_array:
          count_frame_hash_string_len = count_frame_hash_string_len+len(count_frame_hash_array_item)+1
        count_frame_hash_array_len_avg_array.append(int((count_frame_hash_string_len-1)))

        count_yolo_tag_string_len_avg = 0
        for count_yolo_tag_string_len_avg_item in count_yolo_tag_string_len_avg_array:
          count_yolo_tag_string_len_avg = count_yolo_tag_string_len_avg+count_yolo_tag_string_len_avg_item
        print('count_yolo_tag_string_len_avg:'+str(int(count_yolo_tag_string_len_avg/len(count_yolo_tag_string_len_avg_array))))

        count_frame_hash_string_len_avg = 0
        for count_frame_hash_string_len_avg_item in count_frame_hash_array_len_avg_array:
          count_frame_hash_string_len_avg = count_frame_hash_string_len_avg+count_frame_hash_string_len_avg_item
        print('count_frame_hash_string_len_avg:'+str(int(count_frame_hash_string_len_avg/len(count_frame_hash_array_len_avg_array))))

        sent_json = json.dumps({'determine_data_group':determine_data_group,'asset_RFID':asset_RFID_array[determine_data_group],'asset_sensor_RFID':asset_camera_RFID_array[determine_data_group],'frame_hash_array':tuple(frame_hash_array),'yolo_tag_array':tuple(yolo_tag_array),'packet_number':count_send_data_packet,'sensor_type':'camera'})
        client.publish((mqtt_service_channel[1]), sent_json, qos=2)
        scp.put(local_path, recursive=True, remote_path=remote_path)
        
        video_size = os.path.getsize(local_path)
        print('video_size:'+str(video_size))
        
        client.publish((mqtt_service_channel[2]), json.dumps({'determine_data_group':determine_data_group,'asset_RFID':asset_RFID_array[determine_data_group],'asset_sensor_RFID':asset_camera_RFID_array[determine_data_group],'video_path':local_path,'sensor_type':'camera'}) ,qos=2)
        client.loop_stop()
        determine_sensor_start=0
        # cap = cv2.VideoCapture(0)
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_hight)
        # frame_size_tuple=(frame_width, frame_hight)
        # fourcc = cv2.VideoWriter_fourcc(*'FFV1')
        #out = cv2.VideoWriter('./video_org/output_yieldy1.avi', fourcc, fps, frame_size_tuple)
        # client.loop_start()
        # yolo_tag_array = list(yolo_tag_array)
        # yolo_tag_array = []
        # frame_hash_array = list(frame_hash_array)
        # frame_hash_array = []
        # init_determine_n_second = 0
        # break


camera_run_Thread = threading.Thread(target = camera_run)
camera_run_Thread.start()