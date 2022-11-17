// C++ code
//
#include "DHT.h" // Temperature and Humidity Library

#include <Adafruit_BMP085.h> //AirPressure Library

String serialMsg= "";

float rawData; // Any data read from sensors (reduces byte usage)
int soilMoistSensor = A0; // Configurable
int temperatureSensor = 13; // D13 - Configurable
DHT dht(temperatureSensor, DHT11); // To Read Temperature and Humidity
int RaindropSensor = A1; //raindrop input pin
int Turbidity_Pin=A2;
Adafruit_BMP085 bmp;

volatile int flow_frequency; // Measures flow sensor pulses
unsigned int l_hour; // Calculated litres/hour
unsigned char flowsensor = 2; // Sensor Input
unsigned long currentTime;
unsigned long cloopTime;

void setup() {
  /* Moisture Sensor Settings */
  pinMode(soilMoistSensor, INPUT);
  pinMode(flowsensor, INPUT);
  attachInterrupt(0, flow, RISING); // Setup Interrupt
  sei(); // Enable interrupts
  currentTime = millis();
  cloopTime = currentTime;

  digitalWrite(flowsensor, HIGH); // Optional Internal Pull-Up

  /* Temperature and Humidity Settings */
  dht.begin();

  /* Serial */
  Serial.begin(9600);
  
  if (!bmp.begin()) {
  Serial.println("Could not find a valid BMP085 sensor, check wiring!");
  while (1) {}
  }
  
}

void flow () // Interrupt function
{
   flow_frequency++;
}

void readFlowSensor(){
   currentTime = millis();
   // Every second, calculate and print litres/hour
   if(currentTime >= (cloopTime + 1000))
   {
      cloopTime = currentTime; // Updates cloopTime
      // Pulse frequency (Hz) = 7.5Q, Q is flow rate in L/min.
      l_hour = (flow_frequency * 60 / 7.5); // (Pulse frequency x 60 min) / 7.5Q = flowrate in L/hour
      flow_frequency = 0; // Reset Counter
      //Serial.print(l_hour, DEC); // Print litres/hour
      //Serial.println(" L/hour");
      String newData = "flow:"+String(l_hour)+" L/hour"+"$";
      serialMsg += newData;
   }  
}

/* 1.2 Moisture Sensor Function Implementation */
void measureSoilMoist() {
  rawData = analogRead(soilMoistSensor);
  float soilMoistPercentage = -100*(rawData)/1023 + 100; // 0 when completely wet
  //Serial.print("Soil Moisture: "); Serial.print(soilMoistPercentage); Serial.println("%");
  String newData = "soil:"+String(soilMoistPercentage)+" %"+"$";
  serialMsg += newData;
}



/* 2.2 Temperature and Humidity Implementation  */
void measureTemperatureAndHumidity() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  if (isnan(humidity) || isnan(temperature)) {
    //Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  //Serial.print(F("Humidity: ")); Serial.print(humidity); Serial.println("%");
  //Serial.print(F("Temperature: ")); Serial.print(temperature); Serial.println(F("°C"));
  String newData = "humidity:"+String(humidity)+" %"+"$"+
  "temperature:"+String(temperature)+" °C"+"$";
  serialMsg += newData;

}
/*Turbidity START*/
void Turbitidity(){
  float Turbidity_Sensor_Voltage=0;
  int samples=600;
  float ntu=0;
  
  Serial.print("before math:");
  Serial.println( (float)analogRead(Turbidity_Pin) ); 

  for(int i=0; i<samples; i++)
    {
        Turbidity_Sensor_Voltage += ((float)analogRead(Turbidity_Pin)/1023)*5;
    }


  Turbidity_Sensor_Voltage = Turbidity_Sensor_Voltage/samples;
  Turbidity_Sensor_Voltage = round_to_dp(Turbidity_Sensor_Voltage,2);
  //Serial.print("before mathh:");
  //Serial.println(Turbidity_Sensor_Voltage ); 
  if(Turbidity_Sensor_Voltage < 2.5){
      ntu = 3000;
    }else{
      if(Turbidity_Sensor_Voltage > 4.20024637) Turbidity_Sensor_Voltage = 4.20024637;
      ntu = -1120.4*square(Turbidity_Sensor_Voltage)+ 5742.3*Turbidity_Sensor_Voltage - 4352.9; 
    }


  Serial.println(ntu); // print out the value you read:
  Serial.println("hello--------------------");
  Serial.println(Turbidity_Sensor_Voltage );
  delay(500);
}
float round_to_dp( float in_value, int decimal_place )
{
  float multiplier = powf( 10.0f, decimal_place );
  in_value = roundf( in_value * multiplier ) / multiplier;
  return in_value;
}
/*Turbidity END*/
/*AirPressure Start*/
void AirPressure(){
    /*
    Serial.print("Temperature = ");
    Serial.print(bmp.readTemperature());
    Serial.println(" *C");
    
    Serial.print("Pressure = ");
    Serial.print(bmp.readPressure());
    Serial.println(" Pa");
    
    // Calculate altitude assuming 'standard' barometric
    // pressure of 1013.25 millibar = 101325 Pascal
    Serial.print("Altitude = ");
    Serial.print(bmp.readAltitude());
    Serial.println(" meters");

    Serial.print("Pressure at sealevel (calculated) = ");
    Serial.print(bmp.readSealevelPressure());
    Serial.println(" Pa");

  // you can get a more precise measurement of altitude
  // if you know the current sea level pressure which will
  // vary with weather and such. If it is 1015 millibars
  // that is equal to 101500 Pascals.
    Serial.print("Real altitude = ");
    Serial.print(bmp.readAltitude(101500));
    Serial.println(" meters");
    
    Serial.println();
    */
    
    String newData = 
    "airTemperature:"+String(bmp.readTemperature())+" °C"+"$"+
    "pressure:"+String(bmp.readPressure())+" Pa"+"$"+
    "altitude:"+String(bmp.readAltitude())+" m"+"$"+
    "seaLevelPressure:"+String(bmp.readSealevelPressure())+" Pa"+"$"+
    "realAltitude:"+String(bmp.readAltitude(101500))+" m"+"$";
    
    serialMsg += newData;
    delay(500);
}
/*AirPressure END*/

/*
 * Raindrop Sensor
 */
void raindrop(){
  int sensvalue =  analogRead(A1);//1023 == 5v if a raindrop drops on module resistance increases and voltage decreases so this integer value is about voltage
  //float newValue = 1.0/(float)sensvalue;
  float newvalue = (float)abs(sensvalue-1024) * 100.0 / 1024.0;
 // Serial.print("raindrop: %");
  //Serial.println(newvalue); //Regular printing process
  
  String newData = "raindrop:"+String(newvalue)+ " %" + "$";
  serialMsg += newData;

}

/* Main Loop */
void loop() {
  serialMsg = "";
  measureSoilMoist();
  measureTemperatureAndHumidity();
  raindrop();
  //rial.println("----------------------------");

  AirPressure();
  //Turbitidity();
  readFlowSensor();  
  Serial.println(serialMsg);
  delay(1000); // Sleep 1000 ms
}
