// Copyright 2017 Google Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <SPI.h>
#include <avr/power.h>

// This code is for the Pro Micro onboard a serial_sd_mcu PCB.
// It talks to the CPLD over SPI, and provides a USB serial interface.

// It also has some code from standalone_programmer/mcu/mcu.ino to support
// programming the CPLD, but this isn't wired up at the moment.

// Pinout:

// CPLD JTAG port

// TDO = D18 (PF7)
#define TDO_PIN 18
// TMS = D19 (PF6)
#define TMS_PIN 19
// TCK = D20 (PF5)
#define TCK_PIN 20
// TDI = D21 (PF4)
#define TDI_PIN 21

// CPLD SPI port

#define cpld_INT 10
#define cpld_MOSI 16
#define cpld_MISO 14
#define cpld_SCK 15
#define cpld_SS A0

//#define NOISY

void setup() {
  // For some reason the caterina bootloader on Chinese Pro Micro
  // boards doesn't always set the clock prescaler properly.
  clock_prescale_set(clock_div_1);

  // Set pin directions for CPLD JTAG
  pinMode(TDO_PIN, INPUT);
  pinMode(TDI_PIN, INPUT_PULLUP);
  pinMode(TMS_PIN, INPUT_PULLUP);
  // Ideally we would pull this down, but we don't want a conflict
  // with an attached JTAG probe
  pinMode(TCK_PIN, INPUT);
  // In future we'll set TDI, TMS, and TCK as outputs, set TDI=1 and
  // TMS=1, and pulse TCK 5 times to reset the CPLD.

  // Set up USB serial port
  Serial.begin(9600);

  // Set up CPLD SPI interface
  pinMode(cpld_INT, INPUT);
  pinMode(cpld_SS, OUTPUT);
  digitalWrite(cpld_SS, HIGH);
  SPI.begin();
  SPI.beginTransaction(SPISettings(16000000L, MSBFIRST, SPI_MODE0));
}

void loop() {
  // Initiate transfer
  digitalWrite(cpld_SS, LOW);

  // First byte is a status byte
  uint8_t avr_status =
    // bit 1 = 1 if we have a byte to send
    (Serial.available() ? 0x02 : 0x00)
    // bit 0 = 1 if we have buffer space
    | (Serial.availableForWrite() ? 0x01 : 0x00);

  uint8_t cpld_status = SPI.transfer(avr_status);
  // bit 0 of cpld_status = 1 if the cpld has buffer space
  // bit 1 of cpld_status = 1 if the cpld has a byte to send

  uint8_t avr_data = 0;
  if ((cpld_status & 0x01) && (avr_status & 0x02)) {
    // If the CPLD told us it has buffer space,
    // and we told it that we have a byte to send,
    // then send a byte.
    avr_data = (uint8_t)Serial.read();
  }

  uint8_t cpld_data = SPI.transfer(avr_data);
  if ((cpld_status & 0x02) && (avr_status & 0x01)) {
    // If the CPLD told us it has a byte to send,
    // and we told it we have buffer space, then
    // we just received a byte.
    Serial.write(cpld_data);
  }

  // Close transfer
  digitalWrite(cpld_SS, HIGH);
}
