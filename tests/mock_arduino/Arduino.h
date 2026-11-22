#pragma once
#include <stdint.h>
#include <math.h>
#include <stdio.h>
typedef uint8_t byte;
#define A0 0
#define A1 1
#define A2 2
#define A3 3
#define A4 4
#define A5 5
#define INPUT 0
#define DEFAULT 1
#define HEX 16
inline int analogRead(int){return 512;}
inline void analogReference(int){}
inline void delayMicroseconds(int){}
inline void pinMode(int,int){}
inline unsigned long millis(){return 200;}
struct FakeSerial {void begin(int){};template<typename T>void print(T){};template<typename T>void println(T,int){};};
static FakeSerial Serial;
