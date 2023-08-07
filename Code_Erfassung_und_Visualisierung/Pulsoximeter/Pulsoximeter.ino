#include <Arduino.h>
#include "communication.h"


BLEExplorer explorer("VTM 20F", "18:71:05:0e:ce:4b", "ffe0", "ffe4");

void setup() {
  explorer.setup();
}

void loop() {
  explorer.loop();
}
