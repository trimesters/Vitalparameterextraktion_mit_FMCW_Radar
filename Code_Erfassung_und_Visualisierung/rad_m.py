"""
/**************************************************************************************************
 *
 *  @file       dat_m.py
 *  @brief      Data_Management
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

# 
 
###################################################################################################
#                                        L I B R A R I E S                                        #
###################################################################################################

# standart libraries
import time
import threading 

from enum import Enum

import numpy as np

# project libraries
import med_a as mea

from dat_d import *
from rad_d import *
from defines import *

###################################################################################################
#                                          D E F I N E S                                          #
###################################################################################################


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

class Radar_Management: 
        
    def __init__(self, 
                 mediator_: mea.Mediator = None,
                ):

        self.mediator = mediator_
        
        self.frame_arft = None
        self.frame_aaft = None

        self.is_connected = False
        
        self.manage_data_arft = False
        self.manage_data_aaft = False
        
        self.manage_processing_aaft = False
        self.manage_processing_arft_rx_1 = False
        self.manage_processing_arft_rx_2 = False
        self.manage_processing_arft_rx_3 = False
        self.manage_processing_arft_rx_4 = False
        
        self.data_lock = threading.Lock()

    def update_radar_config(self):
        
        if (self.is_connected):

            frame_start = None
            arft_value = 0
            aaft_value = 0
            done_value = RDOT.DONE.value
            
            payload_length = 0
            amount_messages = 0
            self.payload_value = 0

            if (self.manage_data_arft):
                if (frame_start == None):
                    frame_start = RDOT.ARFT.name.encode()
                payload_length = payload_length + PAYLOAD_ARFT
                amount_messages = amount_messages + 1
                arft_value = RDOT.ARFT.value

            if (self.manage_data_aaft):
                if (frame_start == None):
                    frame_start = RDOT.AAFT.name.encode()
                payload_length = payload_length + PAYLOAD_AAFT
                amount_messages = amount_messages + 1
                aaft_value = RDOT.AAFT.value
                
            self.payload_value = done_value | arft_value | aaft_value
                            
            self.mediator.provide_data(self, Objects.UDP_Server, "set_frame_start", frame_start)    
            self.mediator.provide_data(self, Objects.UDP_Server, "set_payload_length", payload_length)
            self.mediator.provide_data(self, Objects.UDP_Server, "set_amount_messages", amount_messages)

    def encode_tcp_package(self, header_, length_, payload_):

        header = bytes(header_, 'utf-8')
        length = length_.to_bytes(4, byteorder='little')
        
        if (length_ > 0):
            payload = (payload_).to_bytes(4, byteorder='little')
            cmd_command = header + length + payload
        else:
            cmd_command = header + length
        
        self.mediator.provide_data(self, Objects.TCP_Client, "set_cmd_command", cmd_command)
        self.decode_tcp_package()
        
    def decode_tcp_package(self):
    
        response = None
             
        while (response != 0):
            response = self.mediator.request_data(self, Objects.TCP_Client, "get_response")
            usleep(TCP_TIMEOUT)
            # TODO: Disconnect after 10 sec or something like that. 
        
    def decode_udp_package(self):  

        while (self.is_connected):
            
            self.decode_udp_server_event.wait()
        
            raw_frame = self.mediator.fast_data_request(self, Objects.UDP_Server)
           
            if (raw_frame is not None):
                
                offset = 0

                if (self.manage_data_arft):
 
                    frame_start = offset + HEADER + LENGTH
                    frame_end = offset + HEADER + LENGTH + PAYLOAD_ARFT
                    offset = frame_end
                    
                    raw_frame_arft = raw_frame[frame_start : frame_end]
                    
                    # Convert the list to a numpy array and compose two bytes to an int16. little-endian 
                    row_data_int16 = np.frombuffer(raw_frame_arft, dtype=np.dtype('<i2'))
                    
                    # Then two float32 values become the real and imaginary part of a complex number. 
                    frame_data_complex64 =  row_data_int16.view(np.int16).astype(np.float32).view(np.complex64)
                    
                    # Transforming the array to a 2D matrix with the size 4 x RX with 256 x SAMPLES points. 
                    # I x 128 + Q x 128
                    with self.data_lock:
                        self.frame_arft = np.reshape(frame_data_complex64, ((RX_N, SAMPLES)))

                if (self.manage_data_aaft):

                    frame_start = offset + HEADER + LENGTH
                    frame_end = offset + HEADER + LENGTH + PAYLOAD_AAFT
                    
                    raw_frame_aaft = raw_frame[frame_start : frame_end]
                    
                    # Convert the list to a numpy array and compose two bytes to an int16. little-endian 
                    row_data_int16 = np.frombuffer(raw_frame_aaft, dtype=np.dtype('<i2'))
                    
                    # Then two float32 values become the real and imaginary part of a complex number. 
                    with self.data_lock:
                        self.frame_aaft =  row_data_int16.view(np.int16).astype(np.float32).view(np.complex64)

                self.mediator.notify(self, "notify_frame_to_process")                 

    def connect_to_radar(self, is_connected):
    
        self.is_connected = is_connected
        
        self.update_radar_config()
    
        if (self.is_connected):
            self.init_radar_config()
        if (self.is_connected):
            self.init_data_stream()

    def init_radar_config(self):
    
        self.mediator.notify(self, "notify_tcp_open")
        
        self.is_connected = self.mediator.request_data(self, Objects.TCP_Client, "get_is_connected")
        
        if (self.is_connected):

            self.encode_tcp_package(TEXT_INIT, LENGTH_INIT, PAYLOAD_INIT)
            self.encode_tcp_package(TEXT_RSET, LENGTH_RSET, RSET.SET_1_256_4_100Hz_TX1.value)
            self.encode_tcp_package(TEXT_RDOT, LENGTH_RDOT, self.payload_value)
        else: 
            print("Error: Socked")
            
    def init_data_stream(self):
        
        self.mediator.notify(self, "notify_udp_open")
        
        self.is_connected = self.mediator.request_data(self, Objects.UDP_Server, "get_is_connected")

        if (self.is_connected):
        
            self.decode_udp_server_threat = threading.Thread(target = self.decode_udp_package)
            self.decode_udp_server_event = threading.Event()
            self.decode_udp_server_threat.start()

    def disconnect_from_radar(self, is_connected):
        
        if (self.is_connected):
        
            self.good_bye_radar()
    
            self.is_connected = is_connected

            self.mediator.notify(self, "notify_tcp_close")
            self.mediator.notify(self, "notify_udp_close")
            
            self.decode_udp_server_event.set()
            self.decode_udp_server_event.clear()
            
            self.decode_udp_server_threat.join()

    def good_bye_radar(self):
        
        self.encode_tcp_package(TEXT_GBYE, LENGTH_GBYE , PAYLOAD_GBYE)
        usleep(GDBY_TIMEOUT)

    def notify_frame_to_manage(self):
        
        self.decode_udp_server_event.set()
        self.decode_udp_server_event.clear()

    def notify_radar_connect(self):
        
        self.connect_to_radar(True)

    def notify_radar_disconnect(self):
    
        self.disconnect_from_radar(False)

    def get_frame_to_process(self):
        
        with self.data_lock:
        
            if (self.manage_processing_arft_rx_1):
                return self.frame_arft[ARFT_RX_1]
            elif (self.manage_processing_arft_rx_2):
                return self.frame_arft[ARFT_RX_2]
            elif (self.manage_processing_arft_rx_3):
                return self.frame_arft[ARFT_RX_3]
            elif (self.manage_processing_arft_rx_4):
                return self.frame_arft[ARFT_RX_4]
            elif (self.manage_processing_aaft):
                return self.frame_aaft

    def get_frame_arft_to_plot(self):
    
        with self.data_lock:
            return self.frame_arft

    def get_frame_aaft_to_plot(self):
    
        with self.data_lock:
            return self.frame_aaft
