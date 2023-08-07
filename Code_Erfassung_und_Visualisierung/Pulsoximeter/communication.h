#ifndef communication_ble_h
#define communication_ble_h

#include <Arduino.h>
#include <ArduinoBLE.h>

class BLEExplorer {
  public:
    BLEExplorer(String target_device_name_, String target_device_address_, String custom_service_UUID_, String custom_characteristic_UUID_);
    void setup();
    void loop();

  private:
    String target_device_name;
    String target_device_address;
    String custom_service_UUID;
    String custom_characteristic_UUID;

    unsigned char data_signal[20];
    int data_length;

    int unknown_1;
    int unknown_2;
    int counter;

    int pr; // pulse_rate
    int spo2; // oxygen saturation
    int ppg; // photoplethysmography
    float pi; // perfusion_index;
    float pt; // parse_time;

    int spo2_wave_val;
    bool sensor_off;

    const byte TOKEN_START = 0xFE;
    const byte TYPE_PO_PARAM = 0x55;
    const byte TYPE_PO_WAVE = 0x56;

    const byte LEN_PO_PARAM = 10;
    const byte LEN_PO_WAVE = 8;

    const int INVALID_PR = 511;
    const byte INVALID_SPO2 = 127;
    const int INVALID_PI = 0;


    void explorerPeripheral(BLEDevice peripheral);
    void exploreService(BLEService service);
    void exploreCharacteristic(BLECharacteristic characteristic);
    void printData(const unsigned char data[], int length);
};
#endif