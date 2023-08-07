"""
/**************************************************************************************************
 *
 *  @file       rad_d.py
 *  @brief      Radar defines
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

# project libraries


###################################################################################################
#                                          D E F I N E S                                          #
###################################################################################################

TX_N = 3
RX_N = 4
ADC_BITS = 16
I_CHANNEL = 1
Q_CHANNEL = 1
SAMPLES = 128 * (I_CHANNEL + Q_CHANNEL)
SWEEPS = 1500

SAMPLING_RATE = 4e6 # Sample rate [sps]:
FRAME_RATE = 100 # F_s [Hz]
PERIOD = 1/FRAME_RATE # 0.010 [s]

FREQUENZ_FC = 61e9  # Carrier Frequency
LIGHT_SPEED = 299792458  # Speed of Light [m / s]
LAMBDA = LIGHT_SPEED / FREQUENZ_FC  # Wavelength [m]

RANGE_MAX = 12.8032 # Rmax [m]:
D_RANGE_MAX = RANGE_MAX / SAMPLES # dR [m]
AZIMUTH_MAX = 85.778 # Maximum = asin(cWAVE_LENGTH_MM/(2 * 2.464mm) = +-85.778°
ELEVATION_MAX = 30   # +- 30° From antenna measurement diagram

BANDWIDTH = LIGHT_SPEED / ( 2 * D_RANGE_MAX ) # Bandwidth [Hz]
SAMPLING_TIME = SAMPLES / ( SAMPLING_RATE ) # Sampling time [s]
SLOPE = BANDWIDTH / SAMPLING_TIME # Slope [Hz/s]
SLOPE_UC = SLOPE * 10**(-12) # Slope [MHz/us] - Units corrected

HEADER = 4
LENGTH = 4

TCP_IP = "192.168.100.201"
TCP_PORT = 6172
TCP_RESPONS = 1
TCP_INTERVAL = 1000

UDP_IP = "192.168.100.1"
UDP_PORT = 4567
UDP_FRAMES = 1
UDP_PAYLOAD = 4096
UDP_INTERVAL = 1

###################################################################################################
#                                        F U N C T I O N S                                        #
###################################################################################################


###################################################################################################
#                                            C L A S S                                            #
###################################################################################################

