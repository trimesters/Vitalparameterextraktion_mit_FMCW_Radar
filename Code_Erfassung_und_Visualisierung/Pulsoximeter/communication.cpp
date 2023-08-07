#include "communication.h"


BLEExplorer::BLEExplorer(String target_device_name_, String target_device_address_, String custom_service_UUID_, String custom_characteristic_UUID_)
{
  target_device_name = target_device_name_;
  target_device_address = target_device_address_;
  custom_service_UUID = custom_service_UUID_;
  custom_characteristic_UUID = custom_characteristic_UUID_;
}

void BLEExplorer::setup() {
  Serial.begin(115200);
  while (!Serial);

  if (!BLE.begin()) {
    while (1);
  }
  BLE.scan();
}

void BLEExplorer::loop() {
  BLEDevice peripheral = BLE.available();

  if (peripheral) {
    if (peripheral.localName() == target_device_name) {
      BLE.stopScan();
      explorerPeripheral(peripheral);
    }
  }
}

void BLEExplorer::explorerPeripheral(BLEDevice peripheral) {
  if (!(peripheral.connect())) {
    return;
  }

  if (!(peripheral.discoverAttributes())) {
    peripheral.disconnect();
    return;
  }

  for (int i = 0; i < peripheral.serviceCount(); i++) {
    BLEService service = peripheral.service(i);
    if (service.uuid() == custom_service_UUID){
      exploreService(service);
    }
  }

  peripheral.disconnect();
}

void BLEExplorer::exploreService(BLEService service) {
  for (int i = 0; i < service.characteristicCount(); i++) {
    BLECharacteristic characteristic = service.characteristic(i);
    if(characteristic.uuid() == custom_characteristic_UUID) {
      exploreCharacteristic(characteristic);
    }
  }
}

void BLEExplorer::exploreCharacteristic(BLECharacteristic characteristic) {
  while(characteristic.uuid() == custom_characteristic_UUID){
    if (characteristic.canSubscribe()) {
      characteristic.subscribe();
      if (characteristic.valueLength() > 0) {
       
        printData(characteristic.value(), characteristic.valueLength());
        
      }
    }
  }
}

void BLEExplorer::printData(const unsigned char data[], int length) {

  String hexString = "";
  for (int i = 0; i < length; i++) {
    if (data[i] < 16) hexString += "0"; // fügt eine führende Null hinzu, wenn der Wert kleiner als 16 ist
    hexString += String(data[i], HEX); // fügt den hexadezimalen Wert des Elements hinzu
  }
  
  if (length > 8 && data[2] == TYPE_PO_PARAM){
    Serial.print(hexString);
    Serial.println();
  }

  
}

