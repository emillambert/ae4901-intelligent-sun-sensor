/* AE4901 lean sensing node. Flash on each Arduino; set BOARD_ID=0 or 1.
   Six ADCs map to +X,-X,+Y,-Y,+Z,-Z. Wiring: Vcc--Rfixed--ADC--LDR--GND.
   The onboard vector is COARSE only. Calibration values are placeholders.
   No Arduino model/physical circuitry has been verified yet. */
#include <Arduino.h>
#ifdef __AVR__
#include <avr/wdt.h>
#endif
#ifndef BOARD_ID
#define BOARD_ID 0
#endif
const byte ADC_PIN[6]={A0,A1,A2,A3,A4,A5};
const float RFIX[6]={30000,30000,30000,30000,30000,30000};
const float R10[6]={25000,25000,25000,25000,25000,25000};
const float GAMMA[6]={.6,.6,.6,.6,.6,.6};
const bool CALIBRATION_VERIFIED=false; // set true ONLY after physical validation
const unsigned long SAMPLE_PERIOD_MS=100;
unsigned long lastSample=0,sequence=0;

uint16_t crc16(const char *s){
  uint16_t crc=0xFFFF;
  while(*s){crc ^= (uint16_t)(uint8_t)*s++ << 8;
    for(byte i=0;i<8;i++)crc=(crc&0x8000)?(crc<<1)^0x1021:(crc<<1);
  }
  return crc;
}
uint16_t median3(byte pin){
  analogRead(pin); // allow mux input to settle
  delayMicroseconds(150);
  uint16_t a=analogRead(pin),b=analogRead(pin),c=analogRead(pin);
  if(a>b){uint16_t t=a;a=b;b=t;}
  if(b>c){uint16_t t=b;b=c;c=t;}
  if(a>b){uint16_t t=a;a=b;b=t;}
  return b;
}
float incidentLux(uint16_t adc,byte i){
  if(adc<2 || adc>1021)return 0.0f;
  // R_LDR=Rfixed*Vadc/(Vcc-Vadc), Vref=Vcc (ratiometric)
  float r=RFIX[i]*float(adc)/float(1023-adc);
  return 10.0f*powf(r/R10[i],-1.0f/GAMMA[i]);
}
void rotateBody(float v[3]){
  const float k=.57735026919f,cs=.98480775301f;
  const float sn=(BOARD_ID==0?.17364817767f:-.17364817767f);
  float d=k*(v[0]+v[1]+v[2]);
  float c[3]={k*(v[2]-v[1]),k*(v[0]-v[2]),k*(v[1]-v[0])};
  for(byte j=0;j<3;j++)v[j]=cs*v[j]+sn*c[j]+k*d*(1-cs);
}
void setup(){
  Serial.begin(115200);
  analogReference(DEFAULT);
  for(byte i=0;i<6;i++)pinMode(ADC_PIN[i],INPUT);
#ifdef __AVR__
  wdt_enable(WDTO_2S);
#endif
}
void loop(){
#ifdef __AVR__
  wdt_reset();
#endif
  unsigned long now=millis();
  if(now-lastSample<SAMPLE_PERIOD_MS)return;
  lastSample=now;
  uint16_t adc[6];float e[6];byte rail=0;
  for(byte i=0;i<6;i++){
    adc[i]=median3(ADC_PIN[i]);
    if(adc[i]<2 || adc[i]>1021)rail|=(1<<i);
    e[i]=incidentLux(adc[i],i);
  }
  float v[3]={e[0]-e[1],e[2]-e[3],e[4]-e[5]};
  float n=sqrtf(v[0]*v[0]+v[1]*v[1]+v[2]*v[2]);
  byte ready=(CALIBRATION_VERIFIED && n>2.0f && rail==0)?1:0;
  if(n>1e-6f){for(byte j=0;j<3;j++)v[j]/=n;rotateBody(v);}
  else v[0]=v[1]=v[2]=0.0f;
  // Packet: SUN4,id,seq,millis,adc[6],vector*10000[3],rail,ready*CRC16
  char out[116];
  snprintf(out,sizeof(out),"SUN4,%u,%lu,%lu,%u,%u,%u,%u,%u,%u,%d,%d,%d,%u,%u",
    (unsigned)BOARD_ID,sequence++,now,
    adc[0],adc[1],adc[2],adc[3],adc[4],adc[5],
    (int)(10000*v[0]),(int)(10000*v[1]),(int)(10000*v[2]),
    (unsigned)rail,(unsigned)ready);
  Serial.print(out);Serial.print('*');Serial.println(crc16(out),HEX);
}
