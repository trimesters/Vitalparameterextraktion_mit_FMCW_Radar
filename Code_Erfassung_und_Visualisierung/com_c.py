"""
/**************************************************************************************************
 *
 *  @file       com_c.py
 *  @brief      TCP_Client
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

class TCP_Client: 
    
    def __init__(self, 
                 mediator: mea.Mediator = None,                
                 tcp_ip = TCP_IP, 
                 tcp_port = TCP_PORT, 
                 tcp_header = HEADER, 
                 tcp_length = LENGTH, 
                 tcp_respons = TCP_RESPONS, 
                 tcp_interval = TCP_INTERVAL):
        
        self.mediator = mediator
        self.response = None
        
        self.tcp_ip = tcp_ip
        self.tcp_port = tcp_port
        
        self.queue_data = Queue(maxsize = 100)
        self.queue_response = Queue(maxsize = 100)
        
        self.is_connected = False

        self.tcp_set_client_values(tcp_header, tcp_length, tcp_respons, tcp_interval)

    def tcp_set_client_values(self, tcp_header, tcp_length, tcp_respons, tcp_interval):

        self._response_len =  tcp_header + tcp_length + tcp_respons

        self.interval = tcp_interval

    def tcp_open(self, is_connected):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.sock.connect((self.tcp_ip, self.tcp_port))
            
        except TimeoutError:
            return False

        self.is_connected = is_connected

        self.mediator.notify(self, "tcp_connected")

        self.recv_timer_event = threading.Thread(target = self.tcp_recv)
        self.recv_timer_event.start()

        self.send_timer_event = threading.Thread(target = self.tcp_send)
        self.send_timer_event.start()
        
    def tcp_recv(self):

        while (self.is_connected):

            readable = self.tcp_available()

            if (self.sock in readable):

                raw_data = b''

                while ( self.is_connected and len(raw_data) < self._response_len ):

                    packet = self.sock.recv(self._response_len) 

                    if (not packet):
                        break
                    
                    raw_data += packet
                    
                self.response = raw_data[8]

                if (raw_data[8] != 0):
                
                    print(f"Error: Command not acknowledged = {raw_data[8]}")  

            usleep(self.interval)
            
    def tcp_available(self):

        readable, _, _ = select.select([self.sock], [], [], 0)
        return readable
    
    def tcp_send(self):

        while (self.is_connected):

            if (self.queue_data.empty() != True):
            
                cmd_to_send = self.queue_data.get()
                self.sock.sendall(cmd_to_send)

            usleep(self.interval)

    def tcp_set_cmd_command(self, data):
        self.queue_data.put(data)
 
    def tcp_get_response(self):
        return self.response
        
    def tcp_get_is_connected(self):
        return self.is_connected

    def tcp_close(self, is_connected):
        
        if (self.is_connected):

            self.is_connected = is_connected

            self.recv_timer_event.join()
            self.send_timer_event.join()

            self.sock.close()

            self.mediator.notify(self, "tcp_disconnected")

