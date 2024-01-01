import serial
import json
import time
import matplotlib.pyplot as plt
import numpy as np
import threading


kalmanPitch = []
kalmanRoll = []
accPitch = []
accRoll = []
PORT = "/dev/cu.usbmodem14201"
BAUD_RATE = 115200
jsonOutput = False

plt.ion() ## Note this correction
fig = plt.figure(figsize=(15, 8))

accPlot = fig.add_subplot(2, 1, 1)
accPlot.set_ylim(-90, 90)

kalmanPlot = fig.add_subplot(2, 1, 2)
kalmanPlot.set_ylim(-90, 90)

def read_imu_data():
  global kalmanPitch, kalmanRoll, accPitch, accRoll, jsonOutput

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
        token = data.split(',')
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
  

def main():
  global kalmanPitch, kalmanRoll

  imu_thread = threading.Thread(target=read_imu_data, name="IMU")
  imu_thread.daemon = True
  imu_thread.start()
  print("imu threa started.")

  # imu_thread.join()
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

    plt.pause(0.0001)

    time.sleep(0.7)
    print("updating graph len: " + str(len(kalmanPitch)) )


if __name__ == "__main__":
  main()