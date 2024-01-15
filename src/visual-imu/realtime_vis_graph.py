import serial
import json
import time
import matplotlib.pyplot as plt
import numpy as np
import threading
import argparse
import socket

kalmanPitch = []
kalmanRoll = []
accPitch = []
accRoll = []
accX = []
accY = []
accZ = []
gyroX = []
gyroY = []
gyroZ = []


# PORT = "/dev/cu.usbmodem14201"
PORT = "COM4"
BAUD_RATE = 115200
jsonOutput = False
params = ""

plt.ion() ## Note this correction
fig = plt.figure(figsize=(18, 9))

accPlot = fig.add_subplot(2, 2, 1)
# accPlot.set_ylim(-90, 90)

kalmanPlot = fig.add_subplot(2, 2, 2)
# kalmanPlot.set_ylim(-90, 90)

accAxisPlot = fig.add_subplot(2, 2, 3)
# accAxisPlot.set_ylim(-90, 90)

gyroAxisPlot = fig.add_subplot(2, 2, 4)
# accAxisPlot.set_ylim(-90, 90)


def init_parse_arg():
    parser = argparse.ArgumentParser(description='IMU - data processing and analysing tools.')

    # remote manager.
    parser.add_argument('-s', '--serial', type=bool, default=False,
                        help='Connect in serial mode for data.')

    # serial baub rate.
    parser.add_argument('-b', '--baud_rate', type=int, default=115200,
                        help='To set the serial baud rate, default is 115200.')

    # serial port
    parser.add_argument('-c', '--serial_port', type=str, default="/dev/cu.usbmodem14201",
                        help='Serial port default is /dev/cu.usbmodem14201.')

    # input file name
    parser.add_argument('-i', '--ip', type=str, default="localhost",
                        help='Remote server IP address to connect.')

    # serial baub rate.
    parser.add_argument('-p', '--sock_port', type=int, default=3033,
                        help='To set remote socket port, default is 3033.')

    args = parser.parse_args()

    return args 


def read_imu_data():
  global kalmanPitch, kalmanRoll, accPitch, accRoll, accX, accY, accZ, gyroX, gyroY, gyroZ, jsonOutput

  ser = serial.Serial(PORT, BAUD_RATE)
  epoch = 0
  while True:
    try:
      # {"imu": {"accelerometer" : { "pitch": -2.95, "roll": 5.08, "x": 0.53, "y": 0.91, "z": 10.22 }, "gyro" : { "x": 0.07, "y": 0.03, "z": -0.07 }, "kalman": { "pitch": -3.20, "roll": 5.25}}}
      data = ser.readline().decode("utf-8") 
      if(jsonOutput == True):
        data = data.replace("\'", "\"")
        # print(data)

        jdata = json.loads(data)
        kpitch = jdata['imu']['kalman']['pitch']
        kroll = jdata['imu']['kalman']['roll']
        acc_pitch = jdata['imu']['accelerometer']['pitch']
        acc_roll = jdata['imu']['accelerometer']['roll']
        epoch = time.time()
        print(str(epoch) + " >> pitch: " + str(kpitch) + ", roll: " + str(kroll))

        kalmanPitch.append(float(kpitch))
        kalmanRoll.append(float(kroll))
        kalmanPitch = kalmanPitch[-3000:] 
        kalmanRoll = kalmanRoll[-3000:]

        accPitch.append(acc_pitch)
        accRoll.append(acc_roll)
        accPitch = accPitch[-3000:]
        accRoll = accRoll[-3000:]
      else:
        # acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, acc_pitch, acc_roll, kalman_pitch, kalman_roll, tempC
        token = data.split(',')

        accX.append(float(token[0]))
        accY.append(float(token[1]))
        accZ.append(float(token[2]))
        accX = accX[-3000:]
        accY = accY[-3000:]
        accZ = accZ[-3000:]

        gyroX.append(float(token[3]))
        gyroY.append(float(token[4]))
        gyroZ.append(float(token[5]))
        gyroX = gyroX[-3000:]
        gyroY = gyroY[-3000:]
        gyroZ = gyroZ[-3000:]

        accPitch.append(float(token[6]))
        accRoll.append(float(token[7]))
        accPitch = accPitch[-3000:]
        accRoll = accRoll[-3000:]

        kalmanPitch.append(float(token[8]))
        kalmanRoll.append(float(token[9]))
        kalmanPitch = kalmanPitch[-3000:] 
        kalmanRoll = kalmanRoll[-3000:]

    except Exception as exp:
      print("Got exception in serial: " + str(exp))
      time.sleep(1)
  

def read_imu_data_sock():
  
  global params, kalmanPitch, kalmanRoll, accPitch, accRoll, accX, accY, accZ, gyroX, gyroY, gyroZ, jsonOutput


  # Create a TCP/IP socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  # Connect the socket to the port where the server is listening
  server_address = (params.ip, params.sock_port)
  print ("connecting to "+ params.ip +" port "+ str(params.sock_port))
  try:
    sock.connect(server_address)
    
    while True:
        # print("Waiting for the data to receive.")
        data = sock.recv(1024).decode("utf-8")
        print('received ::' + str(data))
        if jsonOutput is False:
          try:
            token = data.split(',')
            if(len(token) == 11):
              accX.append(float(token[0]))
              accY.append(float(token[1]))
              accZ.append(float(token[2]))
              accX = accX[-3000:]
              accY = accY[-3000:]
              accZ = accZ[-3000:]

              gyroX.append(float(token[3]))
              gyroY.append(float(token[4]))
              gyroZ.append(float(token[5]))
              gyroX = gyroX[-3000:]
              gyroY = gyroY[-3000:]
              gyroZ = gyroZ[-3000:]

              accPitch.append(float(token[6]))
              accRoll.append(float(token[7]))
              accPitch = accPitch[-3000:]
              accRoll = accRoll[-3000:]

              kalmanPitch.append(float(token[8]))
              kalmanRoll.append(float(token[9]))
              kalmanPitch = kalmanPitch[-3000:] 
              kalmanRoll = kalmanRoll[-3000:]
          except Exception as ex:
            print("Got exception in data handling. " + str(ex))

  finally:
      print('closing socket')
      sock.close()


def main():
  global kalmanPitch, kalmanRoll, accX, accY, accZ, gyroX, gyroY, gyroZ, params

  params = init_parse_arg()

  if(params.serial is True):
    imu_thread = threading.Thread(target=read_imu_data, name="IMU")
    imu_thread.daemon = True
    imu_thread.start()
    print("imu threa started.")
    # imu_thread.join()
  else:
    print("Connecting remote socket.")
    imu_remote_thread = threading.Thread(target=read_imu_data_sock, name="IMU_REMOTE")
    imu_remote_thread.daemon = True
    imu_remote_thread.start()

  '''
    We have to handler the matplot in the main thread. 
    This data ploting is also lagging data read from serial port.
  '''
  while True:
    kalmanPlot.clear()
    kalmanPlot.plot(kalmanPitch, label="Pitch [Kalman]")
    kalmanPlot.plot(kalmanRoll, label="Roll [Kalman]")
    kalmanPlot.legend()
    
    accPlot.clear()
    accPlot.plot(accPitch, label="Pitch [Acc]")
    accPlot.plot(accRoll, label="Roll [Acc]")
    accPlot.legend()

    accAxisPlot.clear()
    accAxisPlot.plot(accX, label="Acc X")
    accAxisPlot.plot(accY, label="Acc Y")
    accAxisPlot.plot(accZ, label="Acc Z")
    accAxisPlot.legend()

    gyroAxisPlot.clear()
    gyroAxisPlot.plot(gyroX, label="Gyro X")
    gyroAxisPlot.plot(gyroY, label="Gyro Y")
    gyroAxisPlot.plot(gyroZ, label="Gyro Z")
    gyroAxisPlot.legend()


    plt.pause(0.0001)

    time.sleep(0.7)
    print("updating graph len: " + str(len(kalmanPitch)) )


if __name__ == "__main__":
  main()