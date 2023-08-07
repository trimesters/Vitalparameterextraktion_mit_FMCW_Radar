"""
/**************************************************************************************************
 *
 *  @file       dat_r.py
 *  @brief      Data_Record
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
import os
import time
import threading 

from queue import Queue
import datetime

import numpy as np

# project libraries
import med_a as mea

from dat_d import *
from defines import *

###################################################################################################
#                                          D E F I N E S                                          #
###################################################################################################

SKIP_X_FRAMES = 1


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

class Data_Record: 
        
    def __init__(self, 
                 mediator_: mea.Mediator = None
                ):

        self.mediator = mediator_
        
        self.is_recording = False
        self.is_radar_connected = False
        self.is_pulsoximeter_connected = False
        
        self.frame_counter = 0
        self.directory_counter = 0

        self.chunk_count = 0
        self.file_prefix = "radar"
        
        self.current_date = str(datetime.datetime.now().date())

    def start_record_data_thread(self):
        # start processing thread
        self.is_recording = True
        self.is_radar_connected = True
        self.is_pulsoximeter_connected = True
        self.record_data_thread = threading.Thread(target = self.rec_record_data)
        self.record_data_event = threading.Event()
        self.record_data_thread.start()
        
    def stop_record_data_thread(self):
        # start processing thread
        self.is_recording = False
        self.is_radar_connected = False
        self.is_pulsoximeter_connected = False
        self.record_data_event.set()
        self.record_data_event.clear()
        self.record_data_thread.join()
        
        self.chunk_count = 0
        self.frame_counter = 0
        
    def rec_record_data(self):
        
        while (self.is_recording):
        
            self.record_data_event.wait()
            
            if (self.is_radar_connected and self.is_pulsoximeter_connected):

                if (SKIP_X_FRAMES < self.frame_counter):
               
                    data = self.mediator.fast_data_request(self, Objects.Data_Process)
                    
                    frame = data[0]
                    
                    frame_cut = frame.shape[0] // 4

                    processed_data = data[1]
                    process_curves = processed_data[PROCESS_CURVES]
                    phase_curve = process_curves[PH_P]
                    #heart_curve = process_curves[HR_P]
                    #breath_curve = process_curves[RR_P]
                    
                    signal = phase_curve
                    
                    process_values = processed_data[PROCESS_VALUES]
                    
                    heart_radar = process_values[HR_P]
                    respiration_radar = process_values[RR_P]

                    heart_uart = self.mediator.fast_data_request(self, Objects.UART_Client)
                    respiration_uart = respiration_radar
                    
                    if (abs(heart_radar - heart_uart) < 5):
                    
                        str_sequence = str(self.directory_counter).zfill(2)
                        directory = f"sequence_uart_{str_sequence}"

                        if not os.path.exists(directory):
                            os.makedirs(directory)

                        str_chunk_count = str(self.chunk_count + 1).zfill(2)

                        file_path = f"{directory}/{self.file_prefix}_chunk_{str_chunk_count}_heart_radar_{heart_radar}_respiration_radar_{respiration_radar}.npz"

                        np.savez(file_path, 
                                 frame=frame[0:frame_cut,:], 
                                 signal=signal, 
                                 heart_uart=heart_uart, 
                                 respiration_uart=respiration_uart, 
                                 heart_radar=heart_radar, 
                                 respiration_radar=respiration_radar)
                    else:
                        
                        print("bad")
                        self.chunk_count -= 1
                        
                    self.chunk_count += 1
                    self.frame_counter = 0
                    
                    if (self.chunk_count > 59):
                        self.directory_counter += 1
                        self.chunk_count = 0

                else: 
                    self.frame_counter += 1

    def notify_frame_to_record(self):
    
        if (self.is_recording):
            self.record_data_event.set()
            self.record_data_event.clear()