import os
import json
import time
import serial
import argparse
import threading
import datetime


PORT = "/dev/cu.usbmodem14201"
BAUD_RATE = 115200
FILE_EXT = ".csv"
MONITORING_INTERVAL = 10.0 # secs
g_data_cache = []
g_file_name = ""
g_mutex_file = threading.Lock()
g_new_file_interval = 1 # mins
g_json_output = False

def gen_new_file(file_prefix):
  global g_file_name, g_new_file_interval, FILE_EXT
  tz = datetime.timezone.utc
  ft = "%Y%m%d_%H%M%S"

  while True:
    with g_mutex_file:
      g_file_name = file_prefix + datetime.datetime.now(tz=tz).strftime(ft) + FILE_EXT
      # print("generate new file name: " + g_file_name)
    time.sleep(g_new_file_interval * 60)


def write_imu_data(log_folder_path):
  global g_data_cache, g_file_name, g_mutex_file, g_json_output

  os.makedirs(log_folder_path, exist_ok=True)
  
  epoch = 0
  while True:
    file_full_path = os.path.join(log_folder_path, g_file_name)
    with g_mutex_file:
      with open(file_full_path, "a") as file_obj:
        if(len(g_data_cache) > 0):
          data = g_data_cache.pop(0)
          if(g_json_output):
            jdata = json.loads(data)
            
            kpitch = jdata['imu']['kalman']['pitch']
            kroll = jdata['imu']['kalman']['roll']
            
            acc_pitch = jdata['imu']['accelerometer']['pitch']
            acc_roll = jdata['imu']['accelerometer']['roll']
            acc_x = jdata['imu']['accelerometer']['x']
            acc_y = jdata['imu']['accelerometer']['x']
            acc_z = jdata['imu']['accelerometer']['x']

            gyro_x = jdata['imu']['gyro']['x']
            gyro_y = jdata['imu']['gyro']['y']
            gyro_z = jdata['imu']['gyro']['z']

            temp_c = jdata['imu']['temp']
            epoch = time.time()
            line = str(epoch) + ", " + str(acc_x) + ", " + str(acc_y) + ", " + str(acc_z) + ", " \
                  + str(gyro_x) + ", " + str(gyro_y) + ", " + str(gyro_z) + ", " \
                  + str(acc_pitch) + ", " + str(acc_roll) + ", " + str(kpitch) + ", " + str(kroll) + ", " \
                  + str(temp_c) \
                  + "\r\n"
          else:
            epoch = time.time()
            line = str(epoch) + ", " + data
          
          # print(line)
          file_obj.write(line)
          file_obj.flush()


def read_imu_data():
  global g_data_cache

  ser = serial.Serial(PORT, BAUD_RATE)

  while True:
    try:
      # {"imu": {"accelerometer" : { "pitch": -2.95, "roll": 5.08, "x": 0.53, "y": 0.91, "z": 10.22 }, "gyro" : { "x": 0.07, "y": 0.03, "z": -0.07 }, "kalman": { "pitch": -3.20, "roll": 5.25}}}
      data = ser.readline().decode("utf-8") 
      data = data.replace("\'", "\"")
      # print(data)
      g_data_cache.append(data)

    except Exception as exp:
      print("Got exception in serial: " + str(exp))
      time.sleep(1)
  

def monitor_operation(interval):
  global g_data_cache

  while True:
    print("Queue length is: " + str(len(g_data_cache)))
    print("Current log file name: " + g_file_name)
    time.sleep(interval)


def main():
  global kalmanPitch, kalmanRoll

  imu_read_thread = threading.Thread(target=read_imu_data, name="IMU")
  imu_read_thread.daemon = True
  imu_read_thread.start()
  print("imu read thread started.")

  file_gen_thread = threading.Thread(target=gen_new_file, name="NEW_FILE", args=("imu_",))
  file_gen_thread.daemon = True
  file_gen_thread.start()
  print("file name generating thread started.")

  imu_write_thread = threading.Thread(target=write_imu_data, name="IMU_DATA_WRITE", args=("../log",))
  imu_write_thread.daemon = True
  imu_write_thread.start()
  print("imu data writing thread started.")

  monitoring_thread = threading.Thread(target=monitor_operation, name="Monitoring_Operation", args=(MONITORING_INTERVAL,))
  monitoring_thread.daemon = True
  monitoring_thread.start()
  print("monitoring operation thread started.")

  imu_read_thread.join()
  imu_write_thread.join()
  file_gen_thread.join()
  monitoring_thread.join()


if __name__ == "__main__":
  main()