#include <DHT.h>
#include <ESP8266WiFi.h>
 
// Hier den ThingSpeak Write API key und die WLAn Netzwerk SSID und das Passwort eintragen
String apiKey = "";
const char* ssid = "";
const char* password = "";

// Die ThingSpeak Server Adresse
const char* server = "api.thingspeak.com";
const int LDR = A0;
const int LED = D4;

// Der Datenpin des Sensors
#define DHTPIN D5
// Der Sensortyp
#define DHTTYPE DHT22 


// Initialisierung
DHT dht(DHTPIN, DHTTYPE);
WiFiClient client;


//Initialiserung beim Programmstart
void setup() 
{
  pinMode(LDR, INPUT);
  pinMode(LED, OUTPUT);
  
  // Baudrate serielle Debugschnittstelle
  Serial.begin(115200);
  delay(10);
  dht.begin();

  WiFi.begin(ssid, password);
 
  Serial.println();
  Serial.println();
  Serial.print("Verbindungsaufnahe zu ");
  Serial.println(ssid);
 
  WiFi.begin(ssid, password);
 
  while (WiFi.status() != WL_CONNECTED) 
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi verbunden");

 delay(1000);
}


// Programmschleife, die wiederkehrend durchlaufend wird
void loop() 
{

  // Einlesen der Sensorwerte
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  int   l = analogRead(LDR);

  // Is Not A Number
  // Überprüfung ob ein Zahlenwert eingelesen wurde
  if (isnan(h) || isnan(t) || isnan(l)) 
  {
    Serial.println("Fehler beim Lesen der Sensor Daten!");
    return;
  }

  // Verbindung zum ThingspeakServer per http Port 80
  if (client.connect(server,80))
  {

    // Datenstring zusammensetzen, Sensorwerte für Feld1 und Feld2
    String postStr = apiKey;
    postStr +="&field1=";
    postStr += String(t);
    postStr +="&field2=";
    postStr += String(h);
    postStr +="&field3=";
    postStr += String(l);
    postStr += "\r\n\r\n";

    // Übergabe der Werte an den Server
    client.print("POST /update HTTP/1.1\n");
    client.print("Host: api.thingspeak.com\n");
    client.print("Connection: close\n");
    client.print("X-THINGSPEAKAPIKEY: "+apiKey+"\n");
    client.print("Content-Type: application/x-www-form-urlencoded\n");
    client.print("Content-Length: ");
    client.print(postStr.length());
    client.print("\n\n");
    client.print(postStr);

    // Debugausgabe
    Serial.print("Temperatur: ");
    Serial.print(t);
    Serial.print(" Luftfeuchtigkeit: ");
    Serial.print(h);
    Serial.print(" Helligkeit: ");
    Serial.print(l);
    Serial.println(" - Sende Daten zu ThingSpeak");

    // Verbindungsabbau zum Server
    client.stop();
  }
  // Debugausgabe
  Serial.println("Warte 5*3*20 secs");
  for( int i = 0; i < 5*3*20; i++)
  {
    digitalWrite(LED, HIGH);
    delay(500);
    digitalWrite(LED, LOW);
    delay(500);
  }

}
