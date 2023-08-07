"""
/**************************************************************************************************
 *
 *  @file       med_m.py
 *  @brief      Connection_Mediator
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
import med_a as mea

from defines import *


###################################################################################################
#                                          D E F I N E S                                          #
###################################################################################################


###################################################################################################
#                                        F U N C T I O N S                                        #
###################################################################################################


###################################################################################################
#                                            C L A S S                                            #
###################################################################################################

class Connection_Mediator(mea.Mediator):
    
    def __init__(self, 
                 gui_surface, 
                 dat_manage,
                 dat_process,
                 dat_record,
                 dat_ai,
                 com_tcp, 
                 com_udp,
                 com_uart
                ):
        
        self.gui_surface = gui_surface
        self.gui_surface.mediator = self
        
        self.manage = dat_manage
        self.manage.mediator = self
        
        self.process = dat_process
        self.process.mediator = self
        
        self.record = dat_record
        self.record.mediator = self
        
        self.ai_lstm = dat_ai
        self.ai_lstm.mediator = self
     
        self.tcp_client = com_tcp
        self.tcp_client.mediator = self
        
        self.udp_server = com_udp
        self.udp_server.mediator = self
        
        self.uart_client = com_uart
        self.uart_client.mediator = self
        
    def notify(self, sender: object, event: str) -> None:
    
        if sender == self.udp_server and event == "notify_frame_to_manage":
            self.manage.notify_frame_to_manage()
            
        elif sender == self.manage and event == "notify_frame_to_process":
            self.process.notify_frame_to_process()
            
        elif sender == self.process and event == "notify_frame_to_record":
            self.record.notify_frame_to_record()

        elif sender == self.gui_surface and event == "notify_radar_connect":
            self.process.notify_radar_connect()
            self.manage.notify_radar_connect()

        elif sender == self.manage and event == "notify_tcp_open":
            self.tcp_client.tcp_open(self.manage.is_connected)
            
        elif sender == self.manage and event == "notify_udp_open":
            self.udp_server.udp_open(self.manage.is_connected)

        elif sender == self.gui_surface and event == "notify_radar_disconnect":
            self.process.notify_radar_disconnect()
            self.manage.notify_radar_disconnect()

        elif sender == self.manage and event == "notify_tcp_close":
            self.tcp_client.tcp_close(self.manage.is_connected)
        
        elif sender == self.manage and event == "notify_udp_close":
            self.udp_server.udp_close(self.manage.is_connected)

        elif sender == self.gui_surface and event == "notify_arft_true_data_update":
            self.manage.manage_data_arft = True

        elif sender == self.gui_surface and event == "notify_arft_false_data_update":
            self.manage.manage_data_arft = False

        elif sender == self.gui_surface and event == "notify_aaft_true_data_update":
            self.manage.manage_data_aaft = True

        elif sender == self.gui_surface and event == "notify_aaft_false_data_update":
            self.manage.manage_data_aaft = False
            
        elif sender == self.gui_surface and event == "notify_start_uart_connection":
            self.uart_client.start_uart_connection(True)

        elif sender == self.gui_surface and event == "notify_stop_uart_connection":
            self.uart_client.stop_uart_connection(False)

        elif sender == self.udp_server and event == "udp_connected":
            self.gui_surface.lb_info_radar_server_1.setText("Connect")

        elif sender == self.udp_server and event == "udp_disconnected":
            self.gui_surface.lb_info_radar_server_1.setText("Disconnect")

        elif sender == self.tcp_client and event == "tcp_connected":
            self.gui_surface.lb_info_radar_client_1.setText("Connect")

        elif sender == self.tcp_client and event == "tcp_disconnected":
            self.gui_surface.lb_info_radar_client_1.setText("Disconnect")

        elif sender == self.gui_surface and event == "notify_record_start":
            self.record.start_record_data_thread()

        elif sender == self.gui_surface and event == "notify_record_stop":
            self.record.stop_record_data_thread()
            
        elif sender == self.gui_surface and event == "notify_signal_peak_true":
            self.process.set_signal_peak = True
            
        elif sender == self.gui_surface and event == "notify_signal_peak_false":
            self.process.set_signal_peak = False

        elif sender == self.gui_surface and event == "notify_manage_processing_aaft":
            self.manage.manage_processing_aaft = True
            self.manage.manage_processing_arft_rx_1 = False
            self.manage.manage_processing_arft_rx_2 = False
            self.manage.manage_processing_arft_rx_3 = False
            self.manage.manage_processing_arft_rx_4 = False
        
        elif sender == self.gui_surface and event == "notify_manage_processing_arft_rx_1":
            self.manage.manage_processing_aaft = False
            self.manage.manage_processing_arft_rx_1 = True
            self.manage.manage_processing_arft_rx_2 = False
            self.manage.manage_processing_arft_rx_3 = False
            self.manage.manage_processing_arft_rx_4 = False
        
        elif sender == self.gui_surface and event == "notify_manage_processing_arft_rx_2":
            self.manage.manage_processing_aaft = False
            self.manage.manage_processing_arft_rx_1 = False
            self.manage.manage_processing_arft_rx_2 = True
            self.manage.manage_processing_arft_rx_3 = False
            self.manage.manage_processing_arft_rx_4 = False
        
        elif sender == self.gui_surface and event == "notify_manage_processing_arft_rx_3":
            self.manage.manage_processing_aaft = False
            self.manage.manage_processing_arft_rx_1 = False
            self.manage.manage_processing_arft_rx_2 = False
            self.manage.manage_processing_arft_rx_3 = True
            self.manage.manage_processing_arft_rx_4 = False
        
        elif sender == self.gui_surface and event == "notify_manage_processing_arft_rx_4":
            self.manage.manage_processing_aaft = False
            self.manage.manage_processing_arft_rx_1 = False
            self.manage.manage_processing_arft_rx_2 = False
            self.manage.manage_processing_arft_rx_3 = False
            self.manage.manage_processing_arft_rx_4 = True
        
        elif sender == self.gui_surface and event == "notify_close":
        
            self.udp_server.is_connected = False
            self.tcp_client.is_connected = False
            
            self.manage.is_running = False
            self.manage.notify_radar_disconnect()

            self.process.is_connected = False
            self.process.is_running = False
            self.process.notify_frame_to_process()

            self.record.is_connected = False
            self.record.is_running = False

    def provide_data(self, sender: object, destination: object, event: str, data: any) -> None:
        
        if (sender == self.manage):
            if (destination == Objects.UDP_Server):
                if (event == "set_payload_length"):
                    self.udp_server.udp_set_payload_length(data)
                elif (event == "set_frame_start"):    
                    self.udp_server.udp_set_frame_start(data)   
                elif (event == "set_amount_messages"):    
                    self.udp_server.udp_set_amount_messages(data)   
                    
            elif (destination == Objects.TCP_Client):  
                if (event == "set_cmd_command"):
                    self.tcp_client.tcp_set_cmd_command(data)

    def request_data(self, sender: object, destination: object, event: str) -> any:
    
        if (sender == self.manage):
            if (destination == Objects.TCP_Client):    
                if (event == "get_response"):
                    return self.tcp_client.tcp_get_response()
                elif (event == "get_is_connected"):
                    return self.tcp_client.tcp_get_is_connected()
            elif (destination == Objects.UDP_Server):   
                if (event == "get_is_connected"):
                    return self.udp_server.udp_get_is_connected()

        elif (sender == self.gui_surface):
            if (destination == Objects.Data_Management):   
                if (event == "get_frame_arft_to_plot"): 
                    return self.manage.get_frame_arft_to_plot()       
                elif (event == "get_frame_aaft_to_plot"): 
                    return self.manage.get_frame_aaft_to_plot()    
            if (destination == Objects.UART_Client):   
                if (event == "get_available_uart_devices"): 
                    return self.uart_client.get_available_uart_devices()   
                
        elif (sender == self.uart_client):
            if (destination == Objects.Control_Panel):   
                if (event == "get_uart_port"): 
                    return self.gui_surface.gui_get_uart_port()       


                
        return None

    def fast_data_request(self, sender: object, destination: object) -> any: 
        
        if (sender == self.manage):
            if (destination == Objects.UDP_Server):    
                return self.udp_server.get_frame_to_manage()
                
        if (sender == self.process):
            if (destination == Objects.Data_Management):    
                return self.manage.get_frame_to_process()
            elif (destination == Objects.Control_Panel):    
                return self.gui_surface.gui_get_signal_peak() 
                
        if (sender == self.gui_surface):
            if (destination == Objects.Data_Process):    
                return self.process.get_processed_data_to_plot()
            elif (destination == Objects.UART_Client):    
                return self.uart_client.get_uart_heart_rate()
            
        if (sender == self.record):
            if (destination == Objects.Data_Process):    
                return self.process.get_processed_data_to_record()
            if (destination == Objects.UART_Client):    
                return self.uart_client.get_heart_rate_to_record()
        return None