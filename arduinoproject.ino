#include "I2Cdev.h"
#include "MPU6050.h"



#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif
MPU6050 accelgyro;

int16_t ax, ay, az;
int16_t gx, gy, gz;
char inChar;
int alarm=0;
#define OUTPUT_READABLE_ACCELGYRO
 
 
void serialEvent() {
  
  while (Serial.available()) {
   inChar = (char)Serial.read();
    }  
}

void setup() {
    #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
        Wire.begin();
    #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
        Fastwire::setup(400, true);
    #endif

    Serial.begin(9600);
    Serial.println("Initializing I2C devices...");
    accelgyro.initialize();
    Serial.println("Testing device connections...");
    Serial.println(accelgyro.testConnection() ? "MPU6050 connection successful" : "MPU6050 connection failed");
    pinMode(4,OUTPUT);
}

void loop() {
  
    accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);


        Serial.print("a/g:\t");
        Serial.print(ax); Serial.print("|");
        Serial.print(ay); Serial.print("|");
        Serial.print(az); Serial.print("|");
        Serial.print(gx); Serial.print("|");
        Serial.print(gy); Serial.print("|");
        Serial.println(gz);
   if(inChar=='A'){
    alarm=1; 
    inChar=""; 
      }

   else if(inChar=='a'){
    alarm=0;
    inChar="";  
      }
    else{
      inChar="";
      }
    if(alarm==1){
  digitalWrite(4,HIGH);
  delay(3 00);
      }
  digitalWrite(4,LOW);
  delay(300);    
}