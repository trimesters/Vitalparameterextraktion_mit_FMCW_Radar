"""
/**************************************************************************************************
 *
 *  @file       com_u.py
 *  @brief      UART_Serial
 *  @author     Florian Kalb B.Sc.
 *
 *  @details    This file contains functions and classes that enable a GUI for 
 *              displaying and processing radar data.
 *  
 *************************************************************************************************/
 """

###################################################################################################
#                                          S O U R C E S                                          #
###################################################################################################

# https://github.com/roger-/FS20F
 
###################################################################################################
#                                        L I B R A R I E S                                        #
###################################################################################################

# standart libraries
import time
import serial
import struct
import threading 

from serial.tools.list_ports import comports

import numpy as np

# project libraries
import med_a as mea

from rad_d import *
from defines import *

###################################################################################################
#                                          D E F I N E S                                          #
###################################################################################################

START_VALUE = 0xfe
TYPE_PARAM = 0x55
TYPE_WAVE  = 0x56

PARAM_LENGTH = 10
WAVE_LENGTH = 8

INVALID_PR = 511
INVALID_SPO2 = 127 
INVALID_PI = 0

UART_TIMEOUT = 1

###################################################################################################
#                                        F U N C T I O N S                                        #
###################################################################################################

def u_second(x):
    return x / 1000000.0

def usleep(x):
    return time.sleep(x / 1000000.0)

###################################################################################################
#                                            C L A S S                                            #
###################################################################################################

class UART_Serial: 
        
    def __init__(self, 
                 mediator_: mea.Mediator = None
                ):

        self.mediator = mediator_
        
        self.is_connected = False
        
        self.uart_serial = None
        
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        
        
        self.pulse_rate = 0
        self.perfusion_index = 0
        self.oxygen_saturation = 0  
        self.ppg = 0
        self.sensor_off = 0
        self.spo2_wave_val = 0
        self.counter = 0
        self.unknown_1 = 0
        
        self.parse_time = time.time()
        
        self.data_lock = threading.Lock()
        
    def start_uart_connection(self, is_connected):
    
        self.is_connected = is_connected

        self.uart_client_thread = threading.Thread(target = self.connect_to_uart_device)
        self.uart_client_thread.start()

    def stop_uart_connection(self, is_connected):
    
        self.is_connected = is_connected
        
        if (self.uart_serial is not None):
            self.uart_serial.close()
            self.uart_serial = None
        else:
            self.mediator.notify(self,"uart_not_connected")

        self.uart_client_thread.join()

    def set_port(self):
        self.port = self.mediator.request_data(self, Objects.Control_Panel, "get_uart_port")
        
    def set_baudrate(self):
        self.baudrate = 115200
                          
    def is_port_available(self, port_name):
        available_ports = [tuple(p) for p in list(comports())]
        return any(port_name in p for p in available_ports)

    def get_available_uart_devices(self):
        available_ports = [tuple(p) for p in list(comports())]
        return available_ports
        
    def get_uart_heart_rate(self):
    
        with self.data_lock:

            return self.pulse_rate
            
    def get_heart_rate_to_record(self):
    
        with self.data_lock:

            return self.pulse_rate
            
    def connect_to_uart_device(self):
    
        self.set_port()
        self.set_baudrate()
    
        if self.is_port_available(self.port):
            try:
                self.uart_serial = serial.Serial(
                    port = self.port,
                    baudrate = self.baudrate,
                    bytesize = self.bytesize,
                    parity = self.parity,
                    stopbits = self.stopbits,
                    )
                                    
                if not self.uart_serial.isOpen():
                    self.uart_serial.open()
                
                self.receive_data_thread = threading.Thread(target = self.receive_and_extract_data_thread)
                self.receive_data_thread.start()
                
            except serial.SerialException as e:
                print(f"Error opening port {self.port}: {str(e)}")
                
        else:
            print(f"Port {self.port} is not available.")
 
    def receive_and_extract_data_thread(self):
    
        buffer = ""
        hex_values = []
        
        while (self.is_connected):
        
            if (self.is_connected):
            
                # Read a byte from the UART stream
                byte = self.uart_serial.read(1)

                # Convert the byte to a character
                char = byte.decode('utf-8', errors='ignore')

                # Check if there is a newline ('\n').
                if char == '\n':
                    # Display the value of the 'buffer' variable and clear it
                    
                    self.parse_raw_data(hex_values) 
                    buffer = ""
                    hex_values = []

                else:
                    # Add the character to the 'buffer' variable
                    buffer += char
                    
                    if len(buffer) == 2:
                        hex_value = int(buffer, 16)  
                        hex_values.append(hex_value)
                        buffer = ""

            usleep(UART_TIMEOUT)
       
    def parse_raw_data(self, buffer):
    
        if not len(buffer) < WAVE_LENGTH:

            if self.sua_check_message(buffer):

                if buffer[2] == TYPE_WAVE:
                    self.parse_wave(buffer)
                    
                elif buffer[2] == TYPE_PARAM:
                    self.parse_param(buffer)
                    
    def sua_check_message(self, start):
    
        if len(start) < 2:
            return 0

        if start[0] == START_VALUE and start[1] in (PARAM_LENGTH, WAVE_LENGTH):
            return start[1]
        return 0
        
    def parse_wave(self, raw):

        self.ppg = raw[3]
        """
        self.sensor_off = bool((raw[4] >> 1) & 1)
        self.spo2_wave_val = raw[5]
        self.counter = raw[6]
        self.unknown_1 = raw[7]
        
        self.parse_time = time.time()
        
        """

    def parse_param(self, raw):
    
        pr = self.byte_to_signed_short(raw[4], raw[3])
        # check for invalid values
        if pr == INVALID_PR:
            pr = self.pulse_rate
            
        with self.data_lock:
            self.pulse_rate = pr
        
        spo2 = raw[5]
        # check for invalid values    
        if spo2 == INVALID_SPO2:
            spo2 = self.oxygen_saturation
            
        """    
        pi = self.byte_to_signed_short(raw[7], raw[6]) 
        # check for invalid values
        if pi == INVALID_PI:
            pi = self.perfusion_index * 1000  
        
        self.counter = raw[8]
        self.unknown_2 = raw[9]

        self.parse_time=time.time()
        
        with self.data_lock:
            self.perfusion_index = pi / 1000
            self.oxygen_saturation = spo2    
        """
        
    def byte_to_signed_short(self, low, high):
        
        return struct.unpack('h', bytearray([low, high]))[0]