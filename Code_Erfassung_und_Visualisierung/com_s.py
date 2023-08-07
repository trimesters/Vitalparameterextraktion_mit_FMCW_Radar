"""
/**************************************************************************************************
 *
 *  @file       com_s.py
 *  @brief      UDP_Server
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
import socket 
import select
import threading 

from queue import Queue

# project libraries
import med_a as mea

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

class UDP_Server: 
    
    def __init__(self, 
                 mediator: mea.Mediator = None,
                 frame_start_ = b"ARFT",
                 udp_ip_ = UDP_IP, 
                 udp_port_ = UDP_PORT, 
                 udp_header_ = HEADER, 
                 udp_length_ = LENGTH, 
                 udp_frames_ = UDP_FRAMES, 
                 udp_payload_ = UDP_PAYLOAD, 
                 udp_interval_ = UDP_INTERVAL):
        
        # update_server         
        self.udp_ip = udp_ip_
        self.udp_port = udp_port_
        self.udp_interval = udp_interval_
        
        # update_message
        self.header = udp_header_
        self.length = udp_length_
        self.frames = udp_frames_
        self.payload = udp_payload_

        self.frame_start = frame_start_
        
        self.mediator = mediator     
        self.message_queue = Queue(maxsize = 10)
        self.is_connected = False
        
        self.udp_update_message()
        
        self.start_time = 0
        self.end_time = 0
        
        
     
    def udp_update_message(self):

        self.message_length = self.header * self.frames + self.length * self.frames + self.payload
        
        self.rx_buffer_values = bytearray(self.message_length * 3) # Buffer * 4 Messages
        self.rx_buffer_length = len(self.rx_buffer_values) 
        
        self.rx_buffer_offset = 0
        self.buffer_pos = 0

    def udp_open(self, is_connected):
    
        try:
   
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.udp_ip, self.udp_port))
            self.is_connected = is_connected
        
            self.mediator.notify(self, "udp_connected")

            self.recv_timer_thread = threading.Thread(target = self.udp_recv)
            self.recv_timer_thread.start()
            
        except OSError:
            print("OSError: [WinError 10048] Normalerweise darf jede Socketadresse (Protokoll, Netzwerkadresse oder Anschluss) nur jeweils einmal verwendet werden")
            self.is_connected = False

    def udp_recv(self):
        
        while (self.is_connected):

            readable = self.udp_available()

            if (self.sock in readable):

                packet = self.sock.recv(self.message_length) 
                length = len(packet)

                #Prevent of buffer overflow
                if ( self.rx_buffer_offset + length > self.rx_buffer_length ):
                    self.rx_buffer_offset = 0

                (self.rx_buffer_values)[self.rx_buffer_offset:] = (bytearray(packet))[:]
                self.rx_buffer_offset += length

                if ( self.rx_buffer_offset > self.message_length and not self.message_queue.full() ):
                    self.udp_load_frame_into_queue()
                
            usleep(self.udp_interval)
        
    def udp_available(self):

        readable, _, _ = select.select([self.sock], [], [], 0)
        return readable
    
    def udp_load_frame_into_queue(self):
    
        self.buffer_pos = self.rx_buffer_values.find(self.frame_start)
        
        if (self.buffer_pos != -1):

            frame_start = self.buffer_pos 
            frame_end = self.buffer_pos + self.message_length
            
            if ( len(self.rx_buffer_values) >= frame_end ):

                self.message_queue.put(self.rx_buffer_values[frame_start : frame_end])
                self.mediator.notify(self, "notify_frame_to_manage")

                self.rx_buffer_values[self.buffer_pos : self.buffer_pos + self.header] = b"FFFF"
                
                self.udp_copy_array_around(frame_end)

    def udp_copy_array_around(self, new_position):
        
        self.rx_buffer_offset = self.rx_buffer_offset - new_position
        
        #Prevent of buffer underflow
        if ( self.rx_buffer_offset < 0 ):
            self.rx_buffer_offset = 0
        else:
            (self.rx_buffer_values)[0:] = (self.rx_buffer_values)[new_position:]

    def udp_close(self, is_connected):
        
        if(self.is_connected):
            
            self.is_connected = is_connected
            self.recv_timer_thread.join()
            self.sock.close()
            self.mediator.notify(self, "udp_disconnected")

    def udp_set_payload_length(self, data):
        self.payload = data
        self.udp_update_message()
            
    def udp_set_frame_start(self, data):
        self.frame_start = data

    def udp_set_amount_messages(self, data):
        self.frames = data
        self.udp_update_message()

    def udp_set_ip(self, data):
        self.udp_ip = data
            
    def udp_set_port(self, data):
        self.udp_port = data
            
    def udp_set_interval(self, data):
        self.udp_interval = data

    def udp_get_data(self):
        return self.message_queue.qsize()
            
    def get_frame_to_manage(self):
        if not self.message_queue.empty():
            return self.message_queue.get()
            
        return None
        
    def udp_get_is_connected(self):
        return self.is_connected