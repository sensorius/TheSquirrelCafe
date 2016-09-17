#include <DHT.h>
#include <ESP8266WiFi.h>
#include <ThingSpeak.h>
#include <Ticker.h>
#include <WiFiUDP.h>

Ticker secondTickr;
volatile int watchdogCount = 0;

// Hier den ThingSpeak Write API key und die WLAn Netzwerk SSID und das Passwort eintragen

char ssid[] = "";  // your network SSID (name) 
char pass[] = "";  // your network password



// SquirrelCafe Weather Data
char writeApiKey[] = "";   // your ThingSpeak write API key
int thingSpeakChannel = 0; // ThngSpeak Channel number


int status = WL_IDLE_STATUS;
WiFiClient  client;
IPAddress ipBroadcast(192, 168, 178, 255);  // your local subnet Broadcast IP address

// A UDP instance to let us send and receive packets over UDP
WiFiUDP Udp;

const int LDR = A0;
const int LED = D4;

// WittyCloud  data pin of sensor
//#define DHTPIN D5

// NodeMCU  data pin of sensor
#define DHTPIN D6

// Sensortyp
#define DHTTYPE DHT21 

int dataCount = 0;


// Initialising
DHT dht(DHTPIN, DHTTYPE);



void ISRwatchdog() {
  
  watchdogCount++;
  
  if( watchdogCount >= 180 ) {
     //Serial.println();
     //Serial.println("the wd bites!");
     ESP.restart();
  }
  
}

// Setup fintction
void setup() 
{
  pinMode(LDR, INPUT);
  pinMode(LED, OUTPUT);
  
  // Baudrate serial Debug Interface
  Serial.begin(115200);
  delay(10);


  secondTickr.attach(1, ISRwatchdog);

  WiFi.begin(ssid, pass);

  ThingSpeak.begin(client);
 
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  while (WiFi.status() != WL_CONNECTED) 
  {
    Serial.print(".");
    digitalWrite(LED, HIGH);
    delay(400);
    digitalWrite(LED, LOW);
    delay(100);
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP-Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("MAC-Address: ");
  Serial.println(WiFi.macAddress());

  dht.begin();
  
  //Wait 30 seconds
 delay(30*1000);
}


// main loop
void loop() 
{
  watchdogCount = 0;
  
  // Read sensor data
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  int   l = analogRead(LDR);

  // Is Not A Number
  // check data read
  if (isnan(h) || isnan(t) || isnan(l)) 
  {
    Serial.println("Error reading sensor data!");
    return;
  }

  // Write to ThingSpeak. There are up to 8 fields in a channel, allowing you to store up to 8 different
  // pieces of information in a channel.  Here, we write to field 1, 2 and 3.

  ThingSpeak.setField(1,t);
  ThingSpeak.setField(2,h);
  ThingSpeak.setField(3,l);
  
 
  // Debugausgabe
  Serial.print("Temperature: ");
  Serial.print(t);
  Serial.print(" Humidity: ");
  Serial.print(h);
  Serial.print(" Light: ");
  Serial.print(l);
  Serial.println(" - Send data to ThingSpeak");


  for( int i = 0; i < 20; i++)
  {
    digitalWrite(LED, HIGH);
    delay(50);
    digitalWrite(LED, LOW);
    delay(50);
  }
  // Write the fields that you've set all at once.
  ThingSpeak.writeFields(thingSpeakChannel, writeApiKey); 
  int resultCode = ThingSpeak.getLastReadStatus();
  dataCount++;
  
  if(resultCode == 200)
  {
     Serial.print("ThingSpeak Write OK "); 
  }
  else
  {
     Serial.print("Error reading message.  Status was: "); 
     Serial.println(resultCode);
  }



   String count = "C:" +String(dataCount);
   String temp = "T:" +String(t);
   String feuchte = " F:" + String(h);
   String result_code = "R:" + String(resultCode);

   char CountData[count.length() + 1];
   count.toCharArray(CountData, count.length() + 1);
   
   char TempData[temp.length() + 1];
   temp.toCharArray(TempData, temp.length() + 1);
 
   char FeuchteData[feuchte.length() + 1];
   feuchte.toCharArray(FeuchteData, feuchte.length() + 1);

   char ResultData[result_code.length() + 1];
   result_code.toCharArray(ResultData, result_code.length() + 1);
  
   Serial.println("Sending UDP broadcast packet");
   Serial.println(WiFi.localIP());
   IPAddress ipBroadcast = WiFi.localIP();
   ipBroadcast[3] = 255;
    
   Udp.beginPacket(ipBroadcast, 4000);
   Udp.write("WeatherData ");
   Udp.write(CountData);
   Udp.write(TempData);
   Udp.write(FeuchteData);
   Udp.write(ResultData);
   Udp.println(" 4242");
   Udp.endPacket(); 


  // Debugausgabe
  Serial.println("Wait for 5*3*20 secs");

  // 5 minute loop
  for( int i = 0; i < 5*60; i++)
  {

    // wait 1 second
    digitalWrite(LED, HIGH);
    delay(990);
    digitalWrite(LED, LOW);
    delay(10);
    watchdogCount = 0;
    yield();

  }
}
