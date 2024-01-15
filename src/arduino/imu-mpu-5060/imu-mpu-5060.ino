#include <Wire.h>
#include <MPU6050.h>
#include <KalmanFilter.h>

#define CALIBRATION_ON true
#define BAUD_RATE 115200

MPU6050 mpu;

KalmanFilter kalmanX(0.001, 0.003, 0.03);
KalmanFilter kalmanY(0.001, 0.003, 0.03);

float accPitch = 0;
float accRoll = 0;

float kalPitch = 0;
float kalRoll = 0;

float tempC = 0.0;

bool outputJson = false; 

void setup() {
  Serial.begin(BAUD_RATE);

  // Initialize MPU6050
  while(!mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_2G)) {
    delay(500);
  }
 
  // Calibrate gyroscope. The calibration must be at rest.
  // If you don't want calibrate, comment this line.
  #ifdef CALIBRATION
  mpu.calibrateGyro();
  #endif
}

void loop() {
  Vector acc = mpu.readNormalizeAccel();
  Vector gyr = mpu.readNormalizeGyro();

  // Calculate Pitch & Roll from accelerometer (deg)
  accPitch = -(atan2(acc.XAxis, sqrt(acc.YAxis*acc.YAxis + acc.ZAxis*acc.ZAxis))*180.0)/M_PI;
  accRoll  = (atan2(acc.YAxis, acc.ZAxis)*180.0)/M_PI;

  // Kalman filter
  kalPitch = kalmanY.update(accPitch, gyr.YAxis);
  kalRoll = kalmanX.update(accRoll, gyr.XAxis);

  tempC = mpu.readTemperature();

  if(outputJson == true) {
    
    Serial.print("{'imu': {");
  
    Serial.print("'accelerometer' : { 'pitch': ");
    Serial.print(accPitch);
    Serial.print(", 'roll': ");
    Serial.print(accRoll);
  
    Serial.print(", 'x': ");
    Serial.print(acc.XAxis);
    Serial.print(", 'y': ");
    Serial.print(acc.YAxis);
    Serial.print(", 'z': ");
    Serial.print(acc.ZAxis);
    Serial.print(" }, ");
  
    Serial.print("'gyro' : { 'x': ");
    Serial.print(gyr.XAxis);
    Serial.print(", 'y': ");
    Serial.print(gyr.YAxis);
    Serial.print(", 'z': ");
    Serial.print(gyr.ZAxis);
    Serial.print(" }, ");
  
    Serial.print("'kalman': { 'pitch': ");
    Serial.print(kalPitch);
    Serial.print(", 'roll': ");
    Serial.print(kalRoll);
    Serial.print("},");  
  
    Serial.print("'temp': ");
    Serial.print(tempC);
  
    Serial.print("}}");  
  
    Serial.println();
  } else {
  
    Serial.print(acc.XAxis);
    Serial.print(", ");
    Serial.print(acc.YAxis);
    Serial.print(", ");
    Serial.print(acc.ZAxis);
    Serial.print(", ");
  
    Serial.print(gyr.XAxis);
    Serial.print(", ");
    Serial.print(gyr.YAxis);
    Serial.print(", ");
    Serial.print(gyr.ZAxis);
    Serial.print(", ");

    Serial.print(accPitch);
    Serial.print(", ");
    Serial.print(accRoll);

    Serial.print(", ");
    Serial.print(kalPitch);
    Serial.print(", ");
    Serial.print(kalRoll);
  
    Serial.print(", ");
    Serial.print(tempC);
  
    Serial.println();
  }
}
