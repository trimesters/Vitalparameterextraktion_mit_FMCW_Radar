"""
/**************************************************************************************************
 *
 *  @file       main.py
 *  @brief      Main
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
from gui_s import *

import com_c as coc
import com_s as cos
import com_u as cou
import med_m as mem
import rad_m as ram
import dat_p as dap
import dat_r as dar
import dat_a as daa

###################################################################################################
#                                          D E F I N E S                                          #
###################################################################################################


###################################################################################################
#                                        F U N C T I O N S                                        #
###################################################################################################

def start_app():
    

    com_tcp = coc.TCP_Client()
    com_udp = cos.UDP_Server()
    com_uart = cou.UART_Serial()   

    rad_manage = ram.Radar_Management()
    dat_process = dap.Data_Process()
    dat_record = dar.Data_Record()
    dat_ai = daa.Artificial_Intelligence()

    app = QtWidgets.QApplication(sys.argv)

    gui_surface = Control_Panel()
    gui_surface.show()
    
    mediator = mem.Connection_Mediator(gui_surface, 
                                       rad_manage, 
                                       dat_process, 
                                       dat_record, 
                                       dat_ai, 
                                       com_tcp, 
                                       com_udp, 
                                       com_uart)
    
    gui_surface.gui_load_start_config()
    
    sys.exit(app.exec())

###################################################################################################
#                                            C L A S S                                            #
###################################################################################################

