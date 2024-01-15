import os
import json
import time
import serial
import argparse
import threading
import datetime
import socket

# PORT = "/dev/cu.usbmodem14201"
PORT = "COM4"
BAUD_RATE = 115200
FILE_EXT = ".dimu"
MONITORING_INTERVAL = 10.0 # secs
g_data_cache = []
g_data_for_client = []
g_file_name = ""
g_mutex_file = threading.Lock()
g_new_file_interval = 60 # mins
g_has_client = False
g_log_folder = "../log"

def init_parse_arg():
    parser = argparse.ArgumentParser(description='IMU - data processing and analysing tools.')

    # remote manager.
    parser.add_argument('-r', '--remote', type=bool, default=True,
                        help='Open the remote manager..')

    # serial baub rate.
    parser.add_argument('-b', '--baud_rate', type=int, default=115200,
                        help='To set the serial baud rate, default is 115200.')

    # serial port
    parser.add_argument('-p', '--port', type=str, default="/dev/cu.usbmodem14201",
                        help='Serial port default is /dev/cu.usbmodem14201.')

    # input file name
    parser.add_argument('-d', '--file_duration', type=int, default=60,
                        help='Interval to generate a new file, default is 60mins.')


    args = parser.parse_args()

    return args  


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
  global g_data_cache, g_file_name, g_mutex_file

  os.makedirs(log_folder_path, exist_ok=True)
  
  epoch = 0
  while True:
    file_full_path = os.path.join(log_folder_path, g_file_name)
    with g_mutex_file:
      with open(file_full_path, "a") as file_obj:
        if(len(g_data_cache) > 0):
          data = g_data_cache.pop(0)
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
      data = ser.readline().decode("utf-8") 
      # print(data)
      g_data_cache.append(data)
      if(g_has_client is True):
        g_data_for_client.append(data)

    except Exception as exp:
      print("Got exception in serial: " + str(exp))
      time.sleep(1)
  

def monitor_operation(interval):
  global g_data_cache, g_data_for_client

  while True:
    # TODO: Current log file size in the verbose
    print("Cache queue length is: " + str(len(g_data_cache)) + " and remote queue len: " + str(len(g_data_for_client)))
    print("Current log file name: " + g_file_name)
    time.sleep(interval)


def remote_client():
  global g_data_for_client, g_has_client
  host = '0.0.0.0'
  port = 3033

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.bind((host, port))
  
  while True:
    try:
      print("Waiting for client to connect")
      sock.listen()
      conn, addr = sock.accept()
      print("New client has been conncted from " + str(addr))
      g_has_client = True
      while g_has_client:
        if(len(g_data_for_client) > 0):
          data = g_data_for_client.pop(0)
          print("Sending this data:: " + data)
          conn.send(data.encode("utf-8"))
        else:
          time.sleep(0.5)
    except Exception as ex:
      print("Socket got exception." + str(ex))
      g_has_client = False
      g_data_for_client.clear()
      time.sleep(1)


def main():
  global kalmanPitch, kalmanRoll, g_log_folder

  params = init_parse_arg()

  imu_read_thread = threading.Thread(target=read_imu_data, name="IMU")
  imu_read_thread.daemon = True
  imu_read_thread.start()
  print("imu read thread started.")

  file_gen_thread = threading.Thread(target=gen_new_file, name="NEW_FILE", args=("imu_",))
  file_gen_thread.daemon = True
  file_gen_thread.start()
  print("file name generating thread started.")

  imu_write_thread = threading.Thread(target=write_imu_data, name="IMU_DATA_WRITE", args=(g_log_folder,))
  imu_write_thread.daemon = True
  imu_write_thread.start()
  print("imu data writing thread started.")

  monitoring_thread = threading.Thread(target=monitor_operation, name="Monitoring_Operation", args=(MONITORING_INTERVAL,))
  monitoring_thread.daemon = True
  monitoring_thread.start()
  print("monitoring operation thread started.")

  remote_client_thread = threading.Thread(target=remote_client, name="Remote_Client")
  remote_client_thread.daemon = True
  remote_client_thread.start()
  print("remote client communication thread started.")

  imu_read_thread.join()
  imu_write_thread.join()
  file_gen_thread.join()
  monitoring_thread.join()
  remote_client_thread.join()


if __name__ == "__main__":
  main()
