/*
  AquaSentinel 1:5 LIVE model - Arduino Nano sensor board (firmware v2, 17 Nov 2026)

  The Nano reads every sensor and drives the beacon and the pump. The Raspberry Pi (USB cable) gets one JSON line
  per second and sends short commands back. You can also watch the lines in the Arduino IDE Serial Monitor at 115200.

  v2 (17 Nov 2026), made for reliable data:
    - DHT11 read every 2.5 s (it cannot answer faster); the last good value is kept for up to 10 s
    - DS18B20: a bad read (-127 / 85) keeps the last good value for up to 5 s, then reports null
    - every line carries "seq" (line counter) and "ck" (checksum) so the Pi can drop a damaged line
    - every line carries "led" (the beacon colour now) so the Pi can re-send a lost command
    - "fw":2, error counters "e_dht" and "e_ds"; commands parsed without String (no memory fragmentation)
    The JSON keys of v1 are unchanged, so older Pi software still works.

  Pins:  A6 pH Po · A1 TDS A · A2 turbidity AO · A3 MQ-3 AO
         D2 DS18B20 (4.7k pull-up to 5 V) · D3 DHT11 · see BOARD_PCB below for the rest
  Libraries (Arduino IDE > Tools > Manage Libraries): OneWire, DallasTemperature, "DHT sensor library" (Adafruit)
  Board: Arduino Nano · Processor: ATmega328P (Old Bootloader) for most clones; try ATmega328P if the upload fails.
  The Pi can flash this itself: tools/flash_nano.sh (uses the ready-made .hex, nothing is compiled on the Pi).

  Commands (end with Enter / newline):
    LED G green | LED R red | LED B blue | LED Y yellow (red+green) | LED W white | LED F fault (red blinking) | LED O off
    PUMP n   run the pump n seconds (0 = stop, max 30)
    PING     answers {"pong":1,"fw":2}
*/
#include <OneWire.h>
#include <DallasTemperature.h>
#include <DHT.h>

#define FW_VERSION 2
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
// pH shown in the Serial Monitor only; the Pi uses ph_v and its own calibration (tools/calibrate.py).
const float PH_CAL_V1 = 2.082, PH_CAL_P1 = 4.0, PH_CAL_V2 = 2.279, PH_CAL_P2 = 9.2;

const unsigned long DHT_EVERY_MS = 2500, DHT_HOLD_MS = 10000, DS_HOLD_MS = 5000;

OneWire oneWire(PIN_DS);
DallasTemperature ds(&oneWire);
DHT dht(PIN_DHT, DHT11);

char beacon = 'G';
unsigned long pumpUntil = 0, lastSample = 0, lastDht = 0, dhtGoodAt = 0, dsGoodAt = 0, seq = 0;
unsigned int errDht = 0, errDs = 0;
float lastTa = NAN, lastRh = NAN, lastTw = NAN;
char cmd[24];
byte cmdLen = 0;
char line[360];
int pos = 0;

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

// ---------- build the line in a buffer, so a checksum can be added ----------
void add(const char *s) { while (*s && pos < (int)sizeof(line) - 1) line[pos++] = *s++; line[pos] = 0; }
void addKey(const char *key) { if (pos > 1) add(","); add("\""); add(key); add("\":"); }
void addNum(const char *key, float v, byte digits, bool ok) {
  addKey(key);
  if (!ok || isnan(v)) { add("null"); return; }
  char b[16]; dtostrf(v, 1, digits, b); add(b);
}
void addLong(const char *key, long v) { addKey(key); char b[12]; ltoa(v, b, 10); add(b); }

void setBeacon(unsigned long now) {
  bool blink = (now / 500) % 2;
  bool r = beacon == 'R' || beacon == 'Y' || beacon == 'W' || (beacon == 'F' && blink);
  bool g = beacon == 'G' || beacon == 'Y' || beacon == 'W';
  bool b = beacon == 'B' || beacon == 'W';
  digitalWrite(PIN_LED_R, r != RGB_COMMON_ANODE);
  digitalWrite(PIN_LED_G, g != RGB_COMMON_ANODE);
  digitalWrite(PIN_LED_B, b != RGB_COMMON_ANODE);
}

void handle(char *c) {
  for (char *p = c; *p; p++) *p = toupper(*p);
  while (*c == ' ') c++;
  if (strncmp(c, "LED ", 4) == 0 && c[4]) {
    if (strchr("GRBYWFO", c[4])) { beacon = c[4]; Serial.println(F("{\"ok\":\"led\"}")); }
  } else if (strncmp(c, "PUMP ", 5) == 0) {
    long s = constrain(atol(c + 5), 0, 30);
    pumpUntil = s ? millis() + s * 1000UL : 0;
    digitalWrite(PIN_PUMP, s ? HIGH : LOW);
    Serial.println(F("{\"ok\":\"pump\"}"));
  } else if (strcmp(c, "PING") == 0) {
    Serial.println(F("{\"pong\":1,\"fw\":2}"));
  }
}

void readSerial() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { if (cmdLen) { cmd[cmdLen] = 0; handle(cmd); } cmdLen = 0; }
    else if (cmdLen < sizeof(cmd) - 1) cmd[cmdLen++] = ch;
  }
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
  readSerial();
  if (pumpUntil && (long)(now - pumpUntil) >= 0) { digitalWrite(PIN_PUMP, LOW); pumpUntil = 0; }
  setBeacon(now);

  // DHT11: at most every 2.5 s; keep the last good value for 10 s
  if (now - lastDht >= DHT_EVERY_MS) {
    lastDht = now;
    float ta = dht.readTemperature(), rh = dht.readHumidity();
    if (!isnan(ta) && !isnan(rh) && rh >= 0 && rh <= 100) { lastTa = ta; lastRh = rh; dhtGoodAt = now; }
    else errDht++;
    readSerial();                                       // the DHT read blocks interrupts briefly: catch up
  }

  if (now - lastSample >= 1000) {
    lastSample = now;
    float vcc = readVcc();
    digitalWrite(PIN_TDS_PWR, HIGH); delay(600);          // TDS on only while it is read (it disturbs pH)
    readSerial();
    float tds = volts(A1, vcc);
    digitalWrite(PIN_TDS_PWR, LOW); delay(300);
    readSerial();
    float ph = volts(A6, vcc), turb = volts(A2, vcc), mq3 = volts(A3, vcc);
    float tw = ds.getTempCByIndex(0); ds.requestTemperatures();      // reads the result of the previous request
    if (tw > -55 && tw < 84.9) { lastTw = tw; dsGoodAt = now; }      // -127 = no sensor, 85 = power-on value
    else errDs++;
    bool twOk = dsGoodAt && now - dsGoodAt <= DS_HOLD_MS;
    bool dhtOk = dhtGoodAt && now - dhtGoodAt <= DHT_HOLD_MS;
    float phVal = PH_CAL_P1 + (ph - PH_CAL_V1) * (PH_CAL_P2 - PH_CAL_P1) / (PH_CAL_V2 - PH_CAL_V1);

    pos = 0; line[0] = 0; add("{");
    addNum("vcc", vcc, 3, true);
    addNum("ph_v", ph, 3, true);
    addNum("ph", phVal, 2, ph > 0.5 && phVal > -1 && phVal < 15);
    addNum("tds_v", tds, 3, true);
    addNum("turb_v", turb, 3, true);
    addNum("mq3_v", mq3, 3, true);
    addLong("ldr_do", digitalRead(PIN_LDR_DO));
    addLong("ph_do", digitalRead(PIN_PH_DO));
    addLong("turb_do", digitalRead(PIN_TURB_DO));
    addLong("mq3_do", digitalRead(PIN_MQ3_DO));
    addNum("t_water", lastTw, 2, twOk);
    addNum("t_air", lastTa, 1, dhtOk);
    addNum("rh", lastRh, 0, dhtOk);
    addLong("pump", digitalRead(PIN_PUMP));
    addLong("up", now / 1000);
    addLong("seq", ++seq);
    addKey("led"); char lb[4] = {'"', beacon, '"', 0}; add(lb);
    addLong("e_dht", errDht);
    addLong("e_ds", errDs);
    addLong("fw", FW_VERSION);
    byte ck = 0;                                       // checksum: sum of every character before ,"ck"
    for (int i = 0; i < pos; i++) ck += (byte)line[i];
    addLong("ck", ck);
    add("}");
    Serial.println(line);
  }
}
