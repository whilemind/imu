import time
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json

PORT = "/dev/cu.usbmodem14201"
BAUD_RATE = 115200

class AnimationPlot:

    def animate(self, i, dataList, ser):
        # ser.write(b'g')                                     # Transmit the char 'g' to receive the Arduino data point
        # data = ser.readline().decode('ascii') # Decode receive Arduino data as a formatted string
        data = ser.readline().decode("utf-8") 
        data = data.replace("\'", "\"")
        # print(data)

        jdata = json.loads(data)
        kpitch = jdata['imu']['kalman']['pitch']
        kroll = jdata['imu']['kalman']['roll']
        print(str(kpitch))
        try:
            arduinoData_float = float(kpitch)   # Convert to float
            dataList.append(arduinoData_float)              # Add to the list holding the fixed number of points to animate
        except:                                             # Pass if data point is bad                               
            pass

        dataList = dataList[-500:]                           # Fix the list size so that the animation plot 'window' is x number of points
        
        ax.clear()                                          # Clear last data frame
        
        self.getPlotFormat()
        ax.plot(dataList)                                   # Plot new data frame
        

    def getPlotFormat(self):
        ax.set_ylim([-90, 90])                              # Set Y axis limit of plot
        ax.set_title("Arduino Data")                        # Set title of figure
        ax.set_ylabel("Value")                              # Set title of y axis

dataList = []                                           # Create empty list variable for later use
                                                        
fig = plt.figure()                                      # Create Matplotlib plots fig is the 'higher level' plot window
ax = fig.add_subplot(111)                               # Add subplot to main fig window

realTimePlot = AnimationPlot()

ser = serial.Serial(PORT, BAUD_RATE)                       # Establish Serial object with COM port and BAUD rate to match Arduino Port/rate
time.sleep(2)                                           # Time delay for Arduino Serial initialization 

# Matplotlib Animation Fuction that takes takes care of real time plot.
# Note that 'fargs' parameter is where we pass in our dataList and Serial object. 
ani = animation.FuncAnimation(fig, realTimePlot.animate, frames=100, fargs=(dataList, ser), interval=10) 

plt.show()                                              # Keep Matplotlib plot persistent on screen until it is closed
ser.close()                                             # Close Serial connection when plot is closed
