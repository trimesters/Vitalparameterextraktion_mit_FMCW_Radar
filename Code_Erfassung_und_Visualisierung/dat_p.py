"""
/**************************************************************************************************
 *
 *  @file       dat_p.py
 *  @brief      Data_Process
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

import numpy as np
import scipy.signal as signal

# project libraries
import med_a as mea

from dat_d import *
from rad_d import *
from defines import *

###################################################################################################
#                                          D E F I N E S                                          #
###################################################################################################

SKIP_X_FRAMES = 50

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

class Data_Process: 
        
    def __init__(self, 
                 mediator_: mea.Mediator = None
                ):

        self.mediator = mediator_
        
        self.is_connected = False
        
        self.process_lock = threading.Lock()

        self.position = 0
        
        dt_c = np.complex64
        self.signal_ring_buffer = np.ones((SWEEPS), dtype=dt_c)
        
        dt_c = np.complex64
        self.frame_ring_buffer = np.ones((SAMPLES, SWEEPS), dtype=dt_c)
        
        dt_i = np.int32
        self.vital_values = np.zeros(((RR_V + HR_V)), dtype=dt_i)
        
        dt_f = np.float32
        self.signal_curves = np.zeros(((RR_V + HR_V + PH_V),SWEEPS), dtype=dt_f)
        
        self.processed_data = [self.signal_curves, self.vital_values, self.position]
        
        # filter limits 
        self.hr_upper_limit = 3.00
        self.hr_lower_limit = 0.80
        self.rr_upper_limit = 0.50
        self.rr_lower_limit = 0.01
        
        self.hr_band_edges = [self.hr_lower_limit, self.hr_upper_limit]
        self.rr_band_edges = [self.rr_lower_limit, self.rr_upper_limit]
        
        # filter order
        self.filter_order = 6

        # filter values
        self.heart_Wn = np.array([self.hr_lower_limit, self.hr_upper_limit]) / (SLOPE_UC / 2)
        self.heart_b, self.heart_a = signal.butter(self.filter_order, self.heart_Wn, btype="bandpass")
        
        self.breath_Wn = np.array([self.rr_lower_limit , self.rr_upper_limit]) / (SLOPE_UC / 2)
        self.breath_b, self.breath_a = signal.butter(self.filter_order, self.breath_Wn, btype="bandpass")

        self.heart_sos = signal.butter(self.filter_order, self.hr_band_edges, btype='band', fs=FRAME_RATE, output='sos')
        self.breath_sos = signal.butter(self.filter_order, self.rr_upper_limit, btype='lowpass', fs=FRAME_RATE, output='sos')
                
        self.set_signal_peak = False
        
        self.frame_counter = 0

    def process_data(self):
        
        while (self.is_connected):
        
            self.process_data_event.wait()
            
            if (self.is_connected):
            
                raw_frame = self.mediator.fast_data_request(self, Objects.Data_Management)
                
                if (raw_frame is not None):
                
                    with self.process_lock:

                        self.rotate_frame_ring_buffer(raw_frame, self.frame_ring_buffer)

                        self.position = self.signal_detection(raw_frame)
                        
                        self.processed_data[PROCESS_POSITION] = self.position  
                        
                        extracted_signal = self.signal_extract(raw_frame, self.position)

                        self.rotate_signal_ring_buffer(extracted_signal, self.signal_ring_buffer)

                        
                        if (SKIP_X_FRAMES < self.frame_counter):
                            
                            phase_signal = self.phase_extract(self.signal_ring_buffer)
                            std_phase_signal = self.standardize_data(phase_signal)
                            heart_signal = self.detect_heartbeat(std_phase_signal)
                            breath_signal = self.detect_breathing(std_phase_signal)

                            self.signal_curves[PH_P] = std_phase_signal
                            self.signal_curves[HR_P] = heart_signal
                            self.signal_curves[RR_P] = breath_signal

                            self.processed_data[PROCESS_CURVES] = self.signal_curves
                            
                            self.vital_values[RR_P] = self.estimate_frequency(breath_signal, FRAME_RATE, ZERO_PADDING)
                            self.vital_values[HR_P] = self.estimate_frequency(heart_signal, FRAME_RATE, ZERO_PADDING)

                            self.processed_data[PROCESS_VALUES] = self.vital_values
                           
                            self.mediator.notify(self, "notify_frame_to_record")

                            self.frame_counter = 0      
                
                        else: 
                            self.frame_counter += 1
                            
                        
   

    def standardize_data(self, buffer):

        mean_val = np.mean(buffer)
        std_val = np.std(buffer)
        
        standardized_buffer = (buffer - mean_val) / std_val
        
        return standardized_buffer
       
    def rotate_signal_ring_buffer(self, sample, buffer):
        buffer[1:] = buffer[:-1]
        buffer[0] = sample
        
    def rotate_frame_ring_buffer(self, sample, buffer):
        buffer[:, 1:] = buffer[:, :-1]
        buffer[:,0] = sample
        
    def signal_detection(self, data):
        # signal_detection
        
        if (self.set_signal_peak == False):
            abs_s = np.abs(data)
            
            abs_s[0:6] = 0 # Eliminate interference coming from the case
            abs_s[SAMPLES - 6:SAMPLES] = 0 # Eliminate interference through overdrive

            max_indices = np.argmax(abs_s)
            
            if (max_indices < self.position - 3):
                max_indices = self.position - 1 
            
            if (max_indices > self.position + 3):
                max_indices = self.position + 1
        else:
            max_indices = self.mediator.fast_data_request(self, Objects.Control_Panel)
        
        return max_indices

    def signal_extract(self, data, position):
        # signal_extract
        extract_signal = data[position]
        
        return extract_signal
        
    def phase_extract(self, data):
        # signal_extract
        angle = np.angle(data)
        unwrap = np.unwrap(angle)
        phase_signal = unwrap * (LAMBDA / (4 * np.pi))
        
        return phase_signal
            
    def detect_heartbeat(self, data):
        # detect_heartbeat

        filter_signal_heart = self.filter_heartbeat_sosfilt(data)
        
        return filter_signal_heart
        
    def filter_heartbeat_lfilter(self, data):

        filter_signal_heart = signal.lfilter(self.heart_b, self.heart_a, data)
        
        return filter_signal_heart

    def filter_heartbeat_sosfilt(self, data):

        filter_signal_heart = signal.sosfilt(self.heart_sos, data)
    
        return filter_signal_heart
        
    def detect_breathing(self, data):

        filter_signal_breath = self.filter_breathing_sosfiltfilt(data)

        return filter_signal_breath
        
    def filter_breathing_lfilter(self, data):

        filter_signal_breath = signal.lfilter(self.breath_b, self.breath_a, data)
        
        return filter_signal_breath
        
    def filter_breathing_sosfiltfilt(self, data):

        filter_signal_breath = signal.sosfiltfilt(self.breath_sos, data)
        
        return filter_signal_breath
            
    def estimate_frequency(self, signal, sample_rate, zeropadding_factor):

        N = len(signal)

        N_padded = 2**int(np.ceil(np.log2(N)) + zeropadding_factor)

        fft_values = np.abs(np.fft.rfft(signal, N_padded))

        fft_freq = np.fft.rfftfreq(N_padded, 1.0 / sample_rate)

        dominant_frequency = fft_freq[np.argmax(fft_values)]

        return dominant_frequency * 60.0

    def notify_frame_to_process(self):
        self.process_data_event.set()
        self.process_data_event.clear()

    def notify_radar_connect(self):

        self.start_data_precessing(True)
        
    def start_data_precessing(self, is_connected):
    
        self.is_connected = is_connected

        self.process_data_thread = threading.Thread(target = self.process_data)
        self.process_data_event = threading.Event()
        self.process_data_thread.start()

    def notify_radar_disconnect(self):
    
        self.stop_data_precessing(False)
        
    def stop_data_precessing(self, is_connected):
    
        self.is_connected = is_connected
        
        self.process_data_event.set()
        self.process_data_event.clear()
        
        self.process_data_thread.join()
        
    def get_processed_data_to_plot(self):
    
        with self.process_lock:

            return self.processed_data

    def get_processed_data_to_record(self):
    
        with self.process_lock:

            return [self.frame_ring_buffer, self.processed_data]