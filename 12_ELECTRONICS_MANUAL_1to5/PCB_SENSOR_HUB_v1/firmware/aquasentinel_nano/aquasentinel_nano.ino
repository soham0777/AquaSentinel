/*
  AquaSentinel 1:5 LIVE model - Arduino Nano sensor board (firmware v1, 11 Nov 2026)

  The Nano reads every sensor and drives the beacon and the pump. The Raspberry Pi (USB cable) gets one JSON line
  per second and sends short commands back. You can also watch the lines in the Arduino IDE Serial Monitor at 115200.

  Pins:  A6 pH Po · A1 TDS A · A2 turbidity AO · A3 MQ-3 AO
         D2 DS18B20 (4.7k pull-up to 5 V) · D3 DHT11 · D4 TDS board power · D5 RGB green · D6 RGB red · D7 pump IN1 · D9 RGB blue
         D8 LDR module DO (digital: 1 or 0, threshold set by the module's blue trimmer)
         D10 pH board Do · D11 turbidity DO · D12 MQ-3 DO  (digital limit outputs, each set by its module trimmer)
         The analog pins are still read and sent (ph_v, turb_v, mq3_v) in case a number is wanted later.
  Libraries (Arduino IDE > Tools > Manage Libraries): OneWire, DallasTemperature, "DHT sensor library" (Adafruit)
  Board: Arduino Nano · Processor: ATmega328P (Old Bootloader) for most clones; try ATmega328P if the upload fails.

  Commands (end with Enter / newline):
    LED G green | LED R red | LED B blue | LED Y yellow (red+green) | LED W white | LED F fault (red blinking) | LED O off
    PUMP n   run the pump n seconds (0 = stop, max 30)
    PING     answers {"pong":1}
*/
#include <OneWire.h>
#include <DallasTemperature.h>
#include <DHT.h>

// 0 = breadboard wiring (tested 12 Nov 2026).  1 = AquaSentinel Sensor Hub PCB v1.2 (104 x 72 mm single-sided board;
// the sensors' 5 V comes from the AUX charger on J12, the Nano itself from the Pi's USB, grounds shared).
#define BOARD_PCB 1
#if BOARD_PCB
// PCB v1.2: J5 TEMP D2 · J4 AIR D3 · J3 LIGHT D4 · J2 TURB D5 · J1 ALC D6 · J6 BEACON G D7 / R D8 / B D9 (220R on board)
//           J7 PUMP D10 (10k pull-down on board) · J8 spare D11 D12 · J9 TDS power A0 + signal A1 · J11 pH A6 (4.7k on board)
const byte PIN_DS = 2, PIN_DHT = 3, PIN_LDR_DO = 4, PIN_TURB_DO = 5, PIN_MQ3_DO = 6, PIN_LED_G = 7, PIN_LED_R = 8,
           PIN_LED_B = 9, PIN_PUMP = 10, PIN_PH_DO = 11, PIN_TDS_PWR = A0;
#else
const byte PIN_DS = 2, PIN_DHT = 3, PIN_TDS_PWR = 4, PIN_LED_G = 5, PIN_LED_R = 6, PIN_PUMP = 7, PIN_LDR_DO = 8, PIN_LED_B = 9,
           PIN_PH_DO = 10, PIN_TURB_DO = 11, PIN_MQ3_DO = 12;
#endif
const bool RGB_COMMON_ANODE = false;   // module common pin marked '-' / GND: false.  Marked '+' / VCC: true
// pH board (ADIY, 9 V supply, output pin "O" -> 4.7k -> A6). PROVISIONAL 2-point calibration, 12 Nov 2026:
// buffer 4.0 -> 2.082 V, buffer 9.2 -> 2.279 V (about 38 mV per pH). Redo with 4.0 / 7.0 / 9.2 before the finale.
const float PH_CAL_V1 = 2.082, PH_CAL_P1 = 4.0, PH_CAL_V2 = 2.279, PH_CAL_P2 = 9.2;
OneWire oneWire(PIN_DS);
DallasTemperature ds(&oneWire);
DHT dht(PIN_DHT, DHT11);

char beacon = 'G';
unsigned long pumpUntil = 0, lastSample = 0;
String cmd;

// Supply voltage from the internal 1.1 V reference: makes the analog readings right even when USB gives 4.7 V, not 5.0 V.
float readVcc() {
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  delay(2);
  ADCSRA |= _BV(ADSC);
  while (bit_is_set(ADCSRA, ADSC)) {}
  long r = ADCL; r |= ADCH << 8;
  return 1125.3 / r;            // 1.1 V * 1023
}

float volts(byte pin, float vcc) {   // average of 32 readings, in volts
  analogRead(pin);                   // first read after switching channel is thrown away
  long s = 0;
  for (byte i = 0; i < 32; i++) { s += analogRead(pin); delayMicroseconds(250); }
  return s * vcc / 1023.0 / 32.0;
}

void printNum(const char *key, float v, byte digits, bool ok) {
  Serial.print('"'); Serial.print(key); Serial.print("\":");
  if (ok) Serial.print(v, digits); else Serial.print("null");
}

void setBeacon(unsigned long now) {
  bool blink = (now / 500) % 2;
  bool r = beacon == 'R' || beacon == 'Y' || beacon == 'W' || (beacon == 'F' && blink);
  bool g = beacon == 'G' || beacon == 'Y' || beacon == 'W';
  bool b = beacon == 'B' || beacon == 'W';
  digitalWrite(PIN_LED_R, r != RGB_COMMON_ANODE);
  digitalWrite(PIN_LED_G, g != RGB_COMMON_ANODE);
  digitalWrite(PIN_LED_B, b != RGB_COMMON_ANODE);
}

void handle(String c) {
  c.trim(); c.toUpperCase();
  if (c.startsWith("LED ") && c.length() >= 5) { beacon = c.charAt(4); Serial.println("{\"ok\":\"led\"}"); }
  else if (c.startsWith("PUMP ")) {
    long s = constrain(c.substring(5).toInt(), 0, 30);
    pumpUntil = s ? millis() + s * 1000UL : 0;
    digitalWrite(PIN_PUMP, s ? HIGH : LOW);
    Serial.println("{\"ok\":\"pump\"}");
  }
  else if (c == "PING") Serial.println("{\"pong\":1}");
}

void setup() {
  pinMode(PIN_TDS_PWR, OUTPUT); digitalWrite(PIN_TDS_PWR, LOW);
  pinMode(PIN_PUMP, OUTPUT);    digitalWrite(PIN_PUMP, LOW);
  pinMode(PIN_LED_G, OUTPUT);   pinMode(PIN_LED_R, OUTPUT);   pinMode(PIN_LED_B, OUTPUT);
  pinMode(PIN_LDR_DO, INPUT);
  pinMode(PIN_PH_DO, INPUT); pinMode(PIN_TURB_DO, INPUT); pinMode(PIN_MQ3_DO, INPUT);
  Serial.begin(115200);
  ds.begin(); ds.setWaitForConversion(false); ds.requestTemperatures();
  dht.begin();
}

void loop() {
  unsigned long now = millis();
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { if (cmd.length()) handle(cmd); cmd = ""; }
    else if (cmd.length() < 20) cmd += ch;
  }
  if (pumpUntil && (long)(now - pumpUntil) >= 0) { digitalWrite(PIN_PUMP, LOW); pumpUntil = 0; }
  setBeacon(now);

  if (now - lastSample >= 1000) {
    lastSample = now;
    float vcc = readVcc();
    digitalWrite(PIN_TDS_PWR, HIGH); delay(600);          // TDS on only while it is read (it disturbs pH)
    float tds = volts(A1, vcc);
    digitalWrite(PIN_TDS_PWR, LOW); delay(300);
    float ph = volts(A6, vcc), turb = volts(A2, vcc), mq3 = volts(A3, vcc);
    float tw = ds.getTempCByIndex(0); ds.requestTemperatures();      // reads the result of the previous request
    float ta = dht.readTemperature(), rh = dht.readHumidity();
    bool twOk = tw > -55 && tw < 84.9;                                // -127 = no sensor, 85 = power-on value

    Serial.print('{');
    printNum("vcc", vcc, 3, true); Serial.print(',');
    printNum("ph_v", ph, 3, true); Serial.print(',');
    float phVal = PH_CAL_P1 + (ph - PH_CAL_V1) * (PH_CAL_P2 - PH_CAL_P1) / (PH_CAL_V2 - PH_CAL_V1);
    printNum("ph", phVal, 2, ph > 0.5 && phVal > -1 && phVal < 15); Serial.print(',');
    printNum("tds_v", tds, 3, true); Serial.print(',');
    printNum("turb_v", turb, 3, true); Serial.print(',');
    printNum("mq3_v", mq3, 3, true); Serial.print(',');
    Serial.print("\"ldr_do\":"); Serial.print(digitalRead(PIN_LDR_DO)); Serial.print(',');
    Serial.print("\"ph_do\":"); Serial.print(digitalRead(PIN_PH_DO)); Serial.print(',');
    Serial.print("\"turb_do\":"); Serial.print(digitalRead(PIN_TURB_DO)); Serial.print(',');
    Serial.print("\"mq3_do\":"); Serial.print(digitalRead(PIN_MQ3_DO)); Serial.print(',');
    printNum("t_water", tw, 2, twOk); Serial.print(',');
    printNum("t_air", ta, 1, !isnan(ta)); Serial.print(',');
    printNum("rh", rh, 0, !isnan(rh)); Serial.print(',');
    Serial.print("\"pump\":"); Serial.print(digitalRead(PIN_PUMP)); Serial.print(',');
    Serial.print("\"up\":"); Serial.print(now / 1000);
    Serial.println('}');
  }
}
