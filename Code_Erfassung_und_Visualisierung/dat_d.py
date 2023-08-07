"""
/**************************************************************************************************
 *
 *  @file       dat_d.py
 *  @brief      Data Defines
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
from enum import Enum

# project libraries


###################################################################################################
#                                          D E F I N E S                                          #
###################################################################################################

################### DATATYPE #######################
D_INT8 = 1
D_INT16 = D_INT8 + D_INT8
D_INT32 = D_INT16 + D_INT16

D_FLOAT32 = D_INT32
D_COMPLEX64 = D_FLOAT32 + D_FLOAT32
D_COMPLEX128 = D_COMPLEX64 + D_COMPLEX64

################ DATA_PROCESSING ###################

ZERO_PADDING = 4

############### MESSAGE_DATATYPE ###################

PROCESS_CURVES = 0
PROCESS_VALUES = 1
PROCESS_POSITION = 2

RR_P = 0
HR_P = 1
PH_P = 2

RR_V = 1
HR_V = 1
PH_V = 1

ARFT_RX_1 = 0
ARFT_RX_2 = 1
ARFT_RX_3 = 2
ARFT_RX_4 = 3

############ MESSAGE_CONFIGURATION #################
HEADER = 4
LENGTH = 4

TEXT_NONE = "NONE"
LENGTH_NONE = 0
PAYLOAD_NONE = 0

TEXT_INIT = "INIT"
LENGTH_INIT = 0
PAYLOAD_INIT = 0

TEXT_GBYE = "GBYE"
LENGTH_GBYE = 0
PAYLOAD_GBYE = 0

TEXT_RSET = "RSET"
LENGTH_RSET = 4

class RSET(Enum):
    SET_1_256_4_100Hz_TX1 = 0
    SET_2_256_4_100Hz_TX1_3 = 1
    SET_3_256_4_100Hz_TX1_2_3 = 2
    SET_4_256_16_50Hz_TX1_3 = 3
    SET_5_256_32_25Hz_TX1_3 = 4

TEXT_RDOT = "RDOT"
LENGTH_RDOT = 4

class RDOT(Enum):
    DONE = 0x20
    ARFT = 0x80
    AAFT = 0x100

PAYLOAD_ARFT = 4096
PAYLOAD_AAFT = 1024

##################### DELAY ########################

CALC_TIMEOUT = 4000
RECO_TIMEOUT = 20000


###################################################################################################
#                                        F U N C T I O N S                                        #
###################################################################################################


###################################################################################################
#                                            C L A S S                                            #
###################################################################################################

