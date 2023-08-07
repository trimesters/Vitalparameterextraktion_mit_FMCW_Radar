"""
/**************************************************************************************************
 *
 *  @file       gui_s.py
 *  @brief      Application
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
import sys

from PyQt6 import QtGui
from PyQt6.QtGui import QPen
from PyQt6.QtGui import QColor

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QPushButton

from PyQt6 import QtCore
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import Qt

from pyqtgraph import PlotWidget
from pyqtgraph import mkColor
from pyqtgraph import GridItem
from pyqtgraph import LegendItem

import numpy as np

import threading

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
    return (x / 1000000.0)

def usleep(x):
    return time.sleep(x / 1000000.0)

###################################################################################################
#                                            C L A S S                                            #
###################################################################################################

class Control_Panel(QMainWindow):
    
    def __init__(self, mediator: mea.Mediator = None):
        
        super().__init__()
        
        self.mediator = mediator
        
        self.gui_setup_ui()

        self.gui_init_plot()
        
        self.gui_uart_timer = QTimer(self)  
        self.gui_uart_timer.timeout.connect(self.gui_update_uart_callback)
        
        self.gui_plot_timer = QTimer(self)  
        self.gui_plot_timer.timeout.connect(self.gui_update_plot_callback)
        
        self.gui_start_gui_timer()

    def gui_init_plot(self):
    
        self.plot_aaft = False

        self.plot_arft = False
        self.plot_arft_rx_1 = False
        self.plot_arft_rx_2 = False
        self.plot_arft_rx_3 = False
        self.plot_arft_rx_4 = False
        
        self.plot_signal = False 
        self.plot_phase_signal = False
        self.plot_heart_signal = False
        self.plot_breath_signal = False
        
        dt_f = np.float32
        
        self.frame_aaft = np.zeros((SAMPLES), dtype=dt_f)
        
        self.frame_arft_rx_1 = np.zeros((SAMPLES), dtype=dt_f)
        self.frame_arft_rx_2 = np.zeros((SAMPLES), dtype=dt_f)
        self.frame_arft_rx_3 = np.zeros((SAMPLES), dtype=dt_f)
        self.frame_arft_rx_4 = np.zeros((SAMPLES), dtype=dt_f)
        
        self.phase_curve = np.zeros((SWEEPS), dtype=dt_f)
        self.heart_curve = np.zeros((SWEEPS), dtype=dt_f)
        self.breath_curve = np.zeros((SWEEPS), dtype=dt_f)
        
    def gui_update_uart_callback(self):
    
        available_devices = self.mediator.request_data(self, Objects.UART_Client, "get_available_uart_devices")
        
        current_index = self.cbb_device_uart_settings_1.currentIndex()
        self.cbb_device_uart_settings_1.clear()

        if (available_devices is not None):
            for device in available_devices:
                self.cbb_device_uart_settings_1.addItem(device[0])

        item_count = self.cbb_device_uart_settings_1.count()
        
        if (item_count > current_index):
            self.cbb_device_uart_settings_1.setCurrentIndex(current_index)
        else:
            self.cbb_device_uart_settings_1.setCurrentIndex(0)
            
    def gui_start_gui_timer(self):
        self.gui_uart_timer.start(GUI_UART_TIMEOUT)  

    def gui_stop_gui_timer(self):
        self.gui_uart_timer.stop()

    def gui_load_start_config(self):

        # Communication
        
        self.btn_radar_connect_1.setEnabled(True)
        self.btn_radar_disconnect_1.setEnabled(False)
        
        self.btn_device_uart_connect_1.setEnabled(True)
        self.btn_device_uart_disconnect_1.setEnabled(False)

        self.cb_data_arft_1.setChecked(True)
        self.cb_data_arft_1.setEnabled(False)
        
        self.gui_cb_communication_aaft_1(False)
        self.gui_cb_communication_arft_1(True)
        
        # Radar
        
        self.cbb_radar_settings_1.setCurrentIndex(0)
        
        # Processing
        
        
        self.rb_processing_arft_rx_1.setChecked(True)
        self.gui_rb_processing_arft_rx_1()
        
        # Plot

        self.gui_rb_arft_plot()
        self.gui_cb_plot_arft_rx_1(True)
        
        self.rb_plot_arft_1.setChecked(True)
        self.cb_plot_arft_rx_1.setChecked(True)
        
        # Record

        self.btn_record_start_1.setEnabled(True)
        self.btn_record_stop_1.setEnabled(False)
         
# Communication
        
    def gui_btn_uart_connect(self):
        
        self.gui_stop_gui_timer()
        
        self.btn_device_uart_connect_1.setEnabled(False)
        self.btn_device_uart_disconnect_1.setEnabled(True)
        self.mediator.notify(self, "notify_start_uart_connection")
    
    def gui_btn_uart_disconnect(self):
    
        self.gui_start_gui_timer()
    
        self.btn_device_uart_connect_1.setEnabled(True)
        self.btn_device_uart_disconnect_1.setEnabled(False)
        self.mediator.notify(self, "notify_stop_uart_connection")
        
    def gui_get_uart_port(self):
    
        return self.cbb_device_uart_settings_1.currentText()
        
    def gui_btn_radar_connect(self):
    
        self.btn_radar_connect_1.setEnabled(False)
        self.btn_radar_disconnect_1.setEnabled(True)
        self.cb_data_aaft_1.setEnabled(False)
        #self.cb_data_arft_1.setEnabled(False)
        self.mediator.notify(self, "notify_radar_connect")
        self.gui_start_plot_timer()
        
    def gui_btn_radar_disconnect(self):
    
        self.btn_radar_connect_1.setEnabled(True)
        self.btn_radar_disconnect_1.setEnabled(False)
        self.cb_data_aaft_1.setEnabled(True)
        #self.cb_data_arft_1.setEnabled(True)
        self.mediator.notify(self, "notify_radar_disconnect")
        self.gui_stop_plot_timer()
        
    def gui_cb_communication_aaft_1(self, state):
    
        if state:
            self.rb_processing_aaft_1.setEnabled(state)
            self.rb_plot_aaft_1.setEnabled(state)
            self.mediator.notify(self, "notify_aaft_true_data_update")

        else:
            self.rb_processing_aaft_1.setEnabled(state)
            self.rb_plot_aaft_1.setEnabled(state)
            self.mediator.notify(self, "notify_aaft_false_data_update")

    def gui_cb_communication_arft_1(self, state):
    
        if state:
            self.rb_processing_arft_rx_1.setEnabled(state)
            self.rb_processing_arft_rx_2.setEnabled(state)
            self.rb_processing_arft_rx_3.setEnabled(state)
            self.rb_processing_arft_rx_4.setEnabled(state)
            self.rb_plot_arft_1.setEnabled(state)
            self.cb_plot_arft_rx_1.setEnabled(state)
            self.cb_plot_arft_rx_2.setEnabled(state)
            self.cb_plot_arft_rx_3.setEnabled(state)
            self.cb_plot_arft_rx_4.setEnabled(state)
            self.mediator.notify(self, "notify_arft_true_data_update")

        else:
            self.rb_processing_arft_rx_1.setEnabled(state)
            self.rb_processing_arft_rx_2.setEnabled(state)
            self.rb_processing_arft_rx_3.setEnabled(state)
            self.rb_processing_arft_rx_4.setEnabled(state)
            self.rb_plot_arft_1.setEnabled(state)
            self.cb_plot_arft_rx_1.setEnabled(state)
            self.cb_plot_arft_rx_2.setEnabled(state)
            self.cb_plot_arft_rx_3.setEnabled(state)
            self.cb_plot_arft_rx_4.setEnabled(state)
            self.mediator.notify(self, "notify_arft_false_data_update")
            
# Radar

# Processing


    def gui_get_signal_peak(self):
        return self.sb_signal_peak_set_1.value()

    def gui_cb_signal_peak_set_1(self, state):
        if state:
            self.mediator.notify(self, "notify_signal_peak_true")

        else:
            self.mediator.notify(self, "notify_signal_peak_false")

    def gui_cb_processing_ai_1(self, state):
        
        a = self.mediator.udp_server.get_frame_to_manage()
        print(self.mediator.udp_server.udp_get_data())
        
        if state:
            print("gui_cb_processing_ai_1 true")

        else:
            print("gui_cb_processing_ai_1 false")
    
    def gui_rb_processing_aaft_1(self):
    
        self.mediator.notify(self, "notify_manage_processing_aaft")

    def gui_rb_processing_arft_rx_1(self):
    
        self.mediator.notify(self, "notify_manage_processing_arft_rx_1")

    def gui_rb_processing_arft_rx_2(self):
    
        self.mediator.notify(self, "notify_manage_processing_arft_rx_2")
            
    def gui_rb_processing_arft_rx_3(self):
    
        self.mediator.notify(self, "notify_manage_processing_arft_rx_3")
            
    def gui_rb_processing_arft_rx_4(self):
    
        self.mediator.notify(self, "notify_manage_processing_arft_rx_4")

# Plot    
            
    def gui_rb_signal_plot(self):
    
        self.plot_aaft = False
        self.plot_arft = False
        self.plot_signal = True
        
        self.plot_arft_rx_1 = False
        self.plot_arft_rx_2 = False
        self.plot_arft_rx_3 = False
        self.plot_arft_rx_4 = False
        
        self.graphicsView.setLabel('left', 'Amplitude', units='E')
        self.graphicsView.setLabel('bottom', 'X-Achse', units='s')
        
        self.legend.clear()
        
        self.legend.addItem(self.plot1, 'Heart')
        self.legend.addItem(self.plot2, 'Breath')
        self.legend.addItem(self.plot3, 'Phase')
        self.legend.addItem(self.plot4, ' ')

        
        self.mediator.notify(self, "plot_signal_true")

        self.gui_set_plot_rx_state(False)
        self.gui_set_plot_signals_state(True)
        
    def gui_rb_aaft_plot(self):

        self.plot_aaft = True
        self.plot_arft = False
        self.plot_signal = False
        
        self.plot_arft_rx_1 = False
        self.plot_arft_rx_2 = False
        self.plot_arft_rx_3 = False
        self.plot_arft_rx_4 = False
        
        self.graphicsView.setLabel('left', 'Amplitude', units='E')
        self.graphicsView.setLabel('bottom', 'Distance', units='m')
        
        self.legend.clear()
        
        self.legend.addItem(self.plot1, 'RX_1-4')
        self.legend.addItem(self.plot2, ' ')
        self.legend.addItem(self.plot3, ' ')
        self.legend.addItem(self.plot4, ' ')
        
        self.mediator.notify(self, "plot_signal_false")

        self.gui_set_plot_rx_state(False)
        self.gui_set_plot_signals_state(False)
    
    def gui_rb_arft_plot(self):
    
        self.plot_aaft = False
        self.plot_arft = True
        self.plot_signal = False
        
        self.plot_arft_rx_1 = False
        self.plot_arft_rx_2 = False
        self.plot_arft_rx_3 = False
        self.plot_arft_rx_4 = False
        
        self.graphicsView.setLabel('left', 'Amplitude', units='E')
        self.graphicsView.setLabel('bottom', 'Distance', units='m')
        
        self.legend.clear()
        
        self.legend.addItem(self.plot1, 'RX_1')
        self.legend.addItem(self.plot2, 'RX_2')
        self.legend.addItem(self.plot3, 'RX_3')
        self.legend.addItem(self.plot4, 'RX_4')
        
        self.mediator.notify(self, "plot_signal_false")

        self.gui_set_plot_rx_state(True)
        self.gui_set_plot_signals_state(False)
        

    def gui_set_plot_signals_state(self, state):
        
        self.cb_plot_phase_signal_1.setEnabled(state)
        self.cb_plot_phase_signal_1.setChecked(False)
        self.cb_plot_heart_signal_1.setEnabled(state)
        self.cb_plot_heart_signal_1.setChecked(False)
        self.cb_plot_breath_signal_1.setEnabled(state)
        self.cb_plot_breath_signal_1.setChecked(False)
        
    def gui_set_plot_rx_state(self, state):
        
        self.cb_plot_arft_rx_1.setEnabled(state)
        self.cb_plot_arft_rx_1.setChecked(False)
        self.cb_plot_arft_rx_2.setEnabled(state)
        self.cb_plot_arft_rx_2.setChecked(False)
        self.cb_plot_arft_rx_3.setEnabled(state)
        self.cb_plot_arft_rx_3.setChecked(False)
        self.cb_plot_arft_rx_4.setEnabled(state)
        self.cb_plot_arft_rx_4.setChecked(False)            
            
    def gui_cb_phase_signal_1_changed(self, state):
    
        if state:
            self.plot_phase_signal = True
        else:
            self.plot_phase_signal = False
        
    def gui_cb_heart_signal_1_changed(self, state):
    
        if state:
            self.plot_heart_signal = True
        else:
            self.plot_heart_signal = False
        
    def gui_cb_breath_signal_1_changed(self, state):
        
        if state:
            self.plot_breath_signal = True
        else:
            self.plot_breath_signal = False
            
    def gui_cb_plot_arft_rx_1(self, state):
    
        if state:
            self.plot_arft_rx_1 = True
        else:
            self.plot_arft_rx_1 = False
            
    def gui_cb_plot_arft_rx_2(self, state):
    
        if state:
            self.plot_arft_rx_2 = True
        else:
            self.plot_arft_rx_2 = False
            
    def gui_cb_plot_arft_rx_3(self, state):
    
        if state:
            self.plot_arft_rx_3 = True
        else:
            self.plot_arft_rx_3 = False
            
    def gui_cb_plot_arft_rx_4(self, state):
    
        if state:
            self.plot_arft_rx_4 = True
        else:
            self.plot_arft_rx_4 = False
            
# Record

    def gui_btn_record_start_1(self):
    
        self.is_recording = True
        
        self.btn_record_start_1.setEnabled(False)
        self.btn_record_stop_1.setEnabled(True)
        
        self.mediator.notify(self, "notify_record_start")

        
    def gui_btn_record_stop_1(self):
    
        self.is_recording = False
        
        self.btn_record_start_1.setEnabled(True)
        self.btn_record_stop_1.setEnabled(False)
        
        self.mediator.notify(self, "notify_record_stop")

# GUI

    def gui_close(self):
        self.mediator.notify(self, "notify_close")
        self.close()
        
    def gui_start_plot_timer(self):
        self.gui_plot_timer.start(GUI_PLOT_TIMEOUT)  

    def gui_stop_plot_timer(self):
        self.gui_plot_timer.stop()  
        

    def gui_get_radar_processing_data(self):
        
        if (self.plot_signal):
            
            data = self.mediator.fast_data_request(self, Objects.Data_Process) 
            
            if (data is not None):
            
                process_curves = data[PROCESS_CURVES]
                self.phase_curve = process_curves[PH_P]
                self.heart_curve = process_curves[HR_P]
                self.breath_curve = process_curves[RR_P]
                
                process_values = data[PROCESS_VALUES]
                heart_value = process_values[HR_P]
                breath_value = process_values[RR_P]
                
                process_position = data[PROCESS_POSITION]
                
                self.lb_radar_hr_2.setText(str(heart_value))
                self.lb_radar_rr_2.setText(str(breath_value))
                self.lb_signal_peak_2.setText(str(process_position))
                
                if (self.plot_heart_signal):
                    self.plot1.setData(self.x_signal, self.heart_curve)
                else:
                    self.plot1.setData(self.x_signal, self.y_signal)
                    
                if (self.plot_breath_signal):
                    self.plot2.setData(self.x_signal, self.breath_curve)
                else:
                    self.plot2.setData(self.x_signal, self.y_signal)
                    
                if (self.plot_phase_signal):
                    self.plot3.setData(self.x_signal, self.phase_curve)
                else:
                    self.plot3.setData(self.x_signal, self.y_signal)
                
                self.plot4.setData(self.x_signal, self.y_signal)

    def gui_get_radar_arft_data(self):
    
        if (self.plot_arft):
        
            data = self.mediator.request_data(self, Objects.Data_Management, "get_frame_arft_to_plot") 
            
            if (data is not None):
            
                self.frame_arft_rx_1 = abs(data[ARFT_RX_1])
                self.frame_arft_rx_2 = abs(data[ARFT_RX_2])
                self.frame_arft_rx_3 = abs(data[ARFT_RX_3])
                self.frame_arft_rx_4 = abs(data[ARFT_RX_4])

                if (self.plot_arft_rx_1):
                    self.plot1.setData(self.x_frame, self.frame_arft_rx_1)
                else:
                    self.plot1.setData(self.x_frame, self.y_frame)

                if (self.plot_arft_rx_2):
                    self.plot2.setData(self.x_frame, self.frame_arft_rx_2)
                else:
                    self.plot2.setData(self.x_frame, self.y_frame)

                if (self.plot_arft_rx_3):
                    self.plot3.setData(self.x_frame, self.frame_arft_rx_3)
                else:
                    self.plot3.setData(self.x_frame, self.y_frame)

                if (self.plot_arft_rx_4):
                    self.plot4.setData(self.x_frame, self.frame_arft_rx_4)
                else:
                    self.plot4.setData(self.x_frame, self.y_frame)

    def gui_get_radar_aaft_data(self):
    
        if (self.plot_aaft):
        
            data = self.mediator.request_data(self, Objects.Data_Management, "get_frame_aaft_to_plot") 
            
            if (data is not None):
                
                self.frame_aaft = abs(data)

                self.plot1.setData(self.x_frame, self.frame_aaft)
                self.plot2.setData(self.x_frame, self.y_frame)
                self.plot3.setData(self.x_frame, self.y_frame)
                self.plot4.setData(self.x_frame, self.y_frame)
        
    def gui_get_uart_heart_rate(self):
        
        data = self.mediator.fast_data_request(self, Objects.UART_Client) 
        
        if (data is not None):
            uart_heart_rate = str(data)
            self.lb_uart_hr_2.setText(uart_heart_rate)

    def gui_update_plot_callback(self):

        self.gui_get_radar_arft_data()
        self.gui_get_radar_aaft_data()
        
        self.gui_get_radar_processing_data()
        
        self.gui_get_uart_heart_rate()

    def gui_setup_ui(self):
        
        self.setObjectName("Application")
        self.resize(756, 877)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(parent=self)
        self.centralwidget.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        self.centralwidget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.NoContextMenu)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 731, 821))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.graphicsView = PlotWidget(parent=self.gridLayoutWidget)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout.addWidget(self.graphicsView, 0, 0, 1, 1)
        self.sb_switchboard = QtWidgets.QTabWidget(parent=self.gridLayoutWidget)
        self.sb_switchboard.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sb_switchboard.sizePolicy().hasHeightForWidth())
        self.sb_switchboard.setSizePolicy(sizePolicy)
        self.sb_switchboard.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        self.sb_switchboard.setElideMode(QtCore.Qt.TextElideMode.ElideLeft)
        self.sb_switchboard.setObjectName("sb_switchboard")
        self.communication = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.communication.sizePolicy().hasHeightForWidth())
        self.communication.setSizePolicy(sizePolicy)
        self.communication.setObjectName("communication")
        self.horizontalLayoutWidget = QtWidgets.QWidget(parent=self.communication)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 681, 351))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(parent=self.horizontalLayoutWidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayoutWidget_6 = QtWidgets.QWidget(parent=self.groupBox)
        self.verticalLayoutWidget_6.setGeometry(QtCore.QRect(10, 40, 213, 301))
        self.verticalLayoutWidget_6.setObjectName("verticalLayoutWidget_6")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_6)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.lb_device_radar_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_6)
        self.lb_device_radar_0.setObjectName("lb_device_radar_0")
        self.horizontalLayout_16.addWidget(self.lb_device_radar_0)
        self.verticalLayout.addLayout(self.horizontalLayout_16)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btn_radar_connect_1 = QtWidgets.QPushButton(parent=self.verticalLayoutWidget_6)
        self.btn_radar_connect_1.setObjectName("btn_radar_connect_1")
        self.horizontalLayout.addWidget(self.btn_radar_connect_1)
        self.btn_radar_disconnect_1 = QtWidgets.QPushButton(parent=self.verticalLayoutWidget_6)
        self.btn_radar_disconnect_1.setObjectName("btn_radar_disconnect_1")
        self.horizontalLayout.addWidget(self.btn_radar_disconnect_1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_24 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_24.setObjectName("horizontalLayout_24")
        self.lb_radar_ip_udp_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_6)
        self.lb_radar_ip_udp_0.setObjectName("lb_radar_ip_udp_0")
        self.horizontalLayout_24.addWidget(self.lb_radar_ip_udp_0)
        self.lb_radar_ip_udp_1 = QtWidgets.QLineEdit(parent=self.verticalLayoutWidget_6)
        self.lb_radar_ip_udp_1.setObjectName("lb_radar_ip_udp_1")
        self.horizontalLayout_24.addWidget(self.lb_radar_ip_udp_1)
        self.verticalLayout.addLayout(self.horizontalLayout_24)
        self.horizontalLayout_41 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_41.setObjectName("horizontalLayout_41")
        self.lb_radar_ip_tcp_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_6)
        self.lb_radar_ip_tcp_0.setObjectName("lb_radar_ip_tcp_0")
        self.horizontalLayout_41.addWidget(self.lb_radar_ip_tcp_0)
        self.lb_radar_ip_tcp_1 = QtWidgets.QLineEdit(parent=self.verticalLayoutWidget_6)
        self.lb_radar_ip_tcp_1.setObjectName("lb_radar_ip_tcp_1")
        self.horizontalLayout_41.addWidget(self.lb_radar_ip_tcp_1)
        self.verticalLayout.addLayout(self.horizontalLayout_41)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_23 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_23.setObjectName("horizontalLayout_23")
        self.lb_device_chest_strap_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_6)
        self.lb_device_chest_strap_0.setIndent(-1)
        self.lb_device_chest_strap_0.setObjectName("lb_device_chest_strap_0")
        self.horizontalLayout_23.addWidget(self.lb_device_chest_strap_0)
        self.verticalLayout.addLayout(self.horizontalLayout_23)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.btn_device_uart_connect_1 = QtWidgets.QPushButton(parent=self.verticalLayoutWidget_6)
        self.btn_device_uart_connect_1.setObjectName("btn_device_uart_connect_1")
        self.horizontalLayout_9.addWidget(self.btn_device_uart_connect_1)
        self.btn_device_uart_disconnect_1 = QtWidgets.QPushButton(parent=self.verticalLayoutWidget_6)
        self.btn_device_uart_disconnect_1.setObjectName("btn_device_uart_disconnect_1")
        self.horizontalLayout_9.addWidget(self.btn_device_uart_disconnect_1)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        self.cbb_device_uart_settings_1 = QtWidgets.QComboBox(parent=self.verticalLayoutWidget_6)
        self.cbb_device_uart_settings_1.setEditable(True)
        self.cbb_device_uart_settings_1.setMaxCount(2147483647)
        self.cbb_device_uart_settings_1.setObjectName("cbb_device_uart_settings_1")
        self.cbb_device_uart_settings_1.addItem("")
        self.verticalLayout.addWidget(self.cbb_device_uart_settings_1)
        self.horizontalLayout_2.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(parent=self.horizontalLayoutWidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayoutWidget_7 = QtWidgets.QWidget(parent=self.groupBox_2)
        self.verticalLayoutWidget_7.setGeometry(QtCore.QRect(10, 40, 201, 301))
        self.verticalLayoutWidget_7.setObjectName("verticalLayoutWidget_7")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_7)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_51 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_51.setObjectName("horizontalLayout_51")
        self.lb_info_radar_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_radar_0.setObjectName("lb_info_radar_0")
        self.horizontalLayout_51.addWidget(self.lb_info_radar_0)
        self.verticalLayout_7.addLayout(self.horizontalLayout_51)
        self.horizontalLayout_39 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_39.setObjectName("horizontalLayout_39")
        self.lb_info_radar_server_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_radar_server_0.setObjectName("lb_info_radar_server_0")
        self.horizontalLayout_39.addWidget(self.lb_info_radar_server_0)
        self.lb_info_radar_server_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_radar_server_1.setObjectName("lb_info_radar_server_1")
        self.horizontalLayout_39.addWidget(self.lb_info_radar_server_1)
        self.verticalLayout_7.addLayout(self.horizontalLayout_39)
        self.horizontalLayout_40 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_40.setObjectName("horizontalLayout_40")
        self.lb_info_radar_client_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_radar_client_0.setObjectName("lb_info_radar_client_0")
        self.horizontalLayout_40.addWidget(self.lb_info_radar_client_0)
        self.lb_info_radar_client_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_radar_client_1.setObjectName("lb_info_radar_client_1")
        self.horizontalLayout_40.addWidget(self.lb_info_radar_client_1)
        self.verticalLayout_7.addLayout(self.horizontalLayout_40)
        self.horizontalLayout_19 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_19.setObjectName("horizontalLayout_19")
        self.lb_info_radar_firmware_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_radar_firmware_0.setObjectName("lb_info_radar_firmware_0")
        self.horizontalLayout_19.addWidget(self.lb_info_radar_firmware_0)
        self.lb_info_radar_firmware_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_radar_firmware_1.setObjectName("lb_info_radar_firmware_1")
        self.horizontalLayout_19.addWidget(self.lb_info_radar_firmware_1)
        self.verticalLayout_7.addLayout(self.horizontalLayout_19)
        self.horizontalLayout_20 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.lb_info_radar_fpga_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_radar_fpga_0.setObjectName("lb_info_radar_fpga_0")
        self.horizontalLayout_20.addWidget(self.lb_info_radar_fpga_0)
        self.lb_info_radar_fpga_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_radar_fpga_1.setObjectName("lb_info_radar_fpga_1")
        self.horizontalLayout_20.addWidget(self.lb_info_radar_fpga_1)
        self.verticalLayout_7.addLayout(self.horizontalLayout_20)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_7.addItem(spacerItem1)
        self.horizontalLayout_54 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_54.setObjectName("horizontalLayout_54")
        self.lb_info_chest_strap_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_chest_strap_0.setObjectName("lb_info_chest_strap_0")
        self.horizontalLayout_54.addWidget(self.lb_info_chest_strap_0)
        self.verticalLayout_7.addLayout(self.horizontalLayout_54)
        self.horizontalLayout_58 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_58.setObjectName("horizontalLayout_58")
        self.lb_info_chest_strap_manufacturer_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_chest_strap_manufacturer_0.setObjectName("lb_info_chest_strap_manufacturer_0")
        self.horizontalLayout_58.addWidget(self.lb_info_chest_strap_manufacturer_0)
        self.lb_info_polar_manufacturer_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_polar_manufacturer_1.setObjectName("lb_info_polar_manufacturer_1")
        self.horizontalLayout_58.addWidget(self.lb_info_polar_manufacturer_1)
        self.verticalLayout_7.addLayout(self.horizontalLayout_58)
        self.horizontalLayout_53 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_53.setObjectName("horizontalLayout_53")
        self.lb_info_chest_strap_model_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_chest_strap_model_0.setObjectName("lb_info_chest_strap_model_0")
        self.horizontalLayout_53.addWidget(self.lb_info_chest_strap_model_0)
        self.lb_info_polar_model_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_polar_model_1.setObjectName("lb_info_polar_model_1")
        self.horizontalLayout_53.addWidget(self.lb_info_polar_model_1)
        self.verticalLayout_7.addLayout(self.horizontalLayout_53)
        self.horizontalLayout_57 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_57.setObjectName("horizontalLayout_57")
        self.lb_info_chest_strap_serial_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_chest_strap_serial_0.setObjectName("lb_info_chest_strap_serial_0")
        self.horizontalLayout_57.addWidget(self.lb_info_chest_strap_serial_0)
        self.lb_info_polar_serial_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_7)
        self.lb_info_polar_serial_1.setObjectName("lb_info_polar_serial_1")
        self.horizontalLayout_57.addWidget(self.lb_info_polar_serial_1)
        self.verticalLayout_7.addLayout(self.horizontalLayout_57)
        self.horizontalLayout_2.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(parent=self.horizontalLayoutWidget)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayoutWidget_8 = QtWidgets.QWidget(parent=self.groupBox_3)
        self.verticalLayoutWidget_8.setGeometry(QtCore.QRect(10, 40, 201, 301))
        self.verticalLayoutWidget_8.setObjectName("verticalLayoutWidget_8")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_8)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_21 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_21.setObjectName("horizontalLayout_21")
        self.lb_data_radar_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_8)
        self.lb_data_radar_0.setObjectName("lb_data_radar_0")
        self.horizontalLayout_21.addWidget(self.lb_data_radar_0)
        self.verticalLayout_8.addLayout(self.horizontalLayout_21)
        self.horizontalLayout_22 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_22.setObjectName("horizontalLayout_22")
        self.cb_data_arft_1 = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_8)
        self.cb_data_arft_1.setObjectName("cb_data_arft_1")
        self.horizontalLayout_22.addWidget(self.cb_data_arft_1)
        self.cb_data_aaft_1 = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_8)
        self.cb_data_aaft_1.setObjectName("cb_data_aaft_1")
        self.horizontalLayout_22.addWidget(self.cb_data_aaft_1)
        self.verticalLayout_8.addLayout(self.horizontalLayout_22)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_8.addItem(spacerItem2)
        self.horizontalLayout_2.addWidget(self.groupBox_3)
        self.sb_switchboard.addTab(self.communication, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(parent=self.tab)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 681, 351))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.groupBox_4 = QtWidgets.QGroupBox(parent=self.horizontalLayoutWidget_2)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayoutWidget_9 = QtWidgets.QWidget(parent=self.groupBox_4)
        self.verticalLayoutWidget_9.setGeometry(QtCore.QRect(10, 40, 321, 301))
        self.verticalLayoutWidget_9.setObjectName("verticalLayoutWidget_9")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_9)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.cbb_radar_settings_1 = QtWidgets.QComboBox(parent=self.verticalLayoutWidget_9)
        self.cbb_radar_settings_1.setEditable(True)
        self.cbb_radar_settings_1.setObjectName("cbb_radar_settings_1")
        self.cbb_radar_settings_1.addItem("")
        self.cbb_radar_settings_1.addItem("")
        self.cbb_radar_settings_1.addItem("")
        self.cbb_radar_settings_1.addItem("")
        self.cbb_radar_settings_1.addItem("")
        self.horizontalLayout_15.addWidget(self.cbb_radar_settings_1)
        self.verticalLayout_9.addLayout(self.horizontalLayout_15)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_9.addItem(spacerItem3)
        self.horizontalLayout_6.addWidget(self.groupBox_4)
        self.groupBox_6 = QtWidgets.QGroupBox(parent=self.horizontalLayoutWidget_2)
        self.groupBox_6.setObjectName("groupBox_6")
        self.verticalLayoutWidget_11 = QtWidgets.QWidget(parent=self.groupBox_6)
        self.verticalLayoutWidget_11.setGeometry(QtCore.QRect(10, 40, 321, 301))
        self.verticalLayoutWidget_11.setObjectName("verticalLayoutWidget_11")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_11)
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.horizontalLayout_18 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.lb_radar_rmax_3 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_3.setObjectName("lb_radar_rmax_3")
        self.horizontalLayout_18.addWidget(self.lb_radar_rmax_3)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_18.addItem(spacerItem4)
        self.lineEdit_3 = QtWidgets.QLineEdit(parent=self.verticalLayoutWidget_11)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.horizontalLayout_18.addWidget(self.lineEdit_3)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_18.addItem(spacerItem5)
        self.lb_radar_rmax_6 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_6.setObjectName("lb_radar_rmax_6")
        self.horizontalLayout_18.addWidget(self.lb_radar_rmax_6)
        self.verticalLayout_10.addLayout(self.horizontalLayout_18)
        self.horizontalLayout_50 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_50.setObjectName("horizontalLayout_50")
        self.lb_radar_rmax_21 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_21.setObjectName("lb_radar_rmax_21")
        self.horizontalLayout_50.addWidget(self.lb_radar_rmax_21)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_50.addItem(spacerItem6)
        self.lineEdit_8 = QtWidgets.QLineEdit(parent=self.verticalLayoutWidget_11)
        self.lineEdit_8.setObjectName("lineEdit_8")
        self.horizontalLayout_50.addWidget(self.lineEdit_8)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_50.addItem(spacerItem7)
        self.lb_radar_rmax_22 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_22.setObjectName("lb_radar_rmax_22")
        self.horizontalLayout_50.addWidget(self.lb_radar_rmax_22)
        self.verticalLayout_10.addLayout(self.horizontalLayout_50)
        self.horizontalLayout_42 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_42.setObjectName("horizontalLayout_42")
        self.lb_radar_rmax_4 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_4.setObjectName("lb_radar_rmax_4")
        self.horizontalLayout_42.addWidget(self.lb_radar_rmax_4)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_42.addItem(spacerItem8)
        self.lineEdit_4 = QtWidgets.QLineEdit(parent=self.verticalLayoutWidget_11)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.horizontalLayout_42.addWidget(self.lineEdit_4)
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_42.addItem(spacerItem9)
        self.lb_radar_rmax_7 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_7.setObjectName("lb_radar_rmax_7")
        self.horizontalLayout_42.addWidget(self.lb_radar_rmax_7)
        self.verticalLayout_10.addLayout(self.horizontalLayout_42)
        self.horizontalLayout_43 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_43.setObjectName("horizontalLayout_43")
        self.lb_radar_rmax_5 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_5.setObjectName("lb_radar_rmax_5")
        self.horizontalLayout_43.addWidget(self.lb_radar_rmax_5)
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_43.addItem(spacerItem10)
        self.lineEdit_5 = QtWidgets.QLineEdit(parent=self.verticalLayoutWidget_11)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.horizontalLayout_43.addWidget(self.lineEdit_5)
        spacerItem11 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_43.addItem(spacerItem11)
        self.lb_radar_rmax_8 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_8.setObjectName("lb_radar_rmax_8")
        self.horizontalLayout_43.addWidget(self.lb_radar_rmax_8)
        self.verticalLayout_10.addLayout(self.horizontalLayout_43)
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.lb_plot_rmax_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_plot_rmax_1.setObjectName("lb_plot_rmax_1")
        self.horizontalLayout_17.addWidget(self.lb_plot_rmax_1)
        spacerItem12 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_17.addItem(spacerItem12)
        self.lineEdit_6 = QtWidgets.QLineEdit(parent=self.verticalLayoutWidget_11)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.horizontalLayout_17.addWidget(self.lineEdit_6)
        spacerItem13 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_17.addItem(spacerItem13)
        self.lb_radar_rmax_11 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_11.setObjectName("lb_radar_rmax_11")
        self.horizontalLayout_17.addWidget(self.lb_radar_rmax_11)
        self.verticalLayout_10.addLayout(self.horizontalLayout_17)
        spacerItem14 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_10.addItem(spacerItem14)
        self.horizontalLayout_44 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_44.setObjectName("horizontalLayout_44")
        self.lb_radar_rmax_9 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_9.setObjectName("lb_radar_rmax_9")
        self.horizontalLayout_44.addWidget(self.lb_radar_rmax_9)
        self.lb_plot_rmax_3 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_plot_rmax_3.setObjectName("lb_plot_rmax_3")
        self.horizontalLayout_44.addWidget(self.lb_plot_rmax_3)
        self.lb_radar_rmax_10 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_10.setObjectName("lb_radar_rmax_10")
        self.horizontalLayout_44.addWidget(self.lb_radar_rmax_10)
        self.verticalLayout_10.addLayout(self.horizontalLayout_44)
        self.horizontalLayout_45 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_45.setObjectName("horizontalLayout_45")
        self.lb_plot_dr_3 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_plot_dr_3.setObjectName("lb_plot_dr_3")
        self.horizontalLayout_45.addWidget(self.lb_plot_dr_3)
        self.lb_plot_dr_4 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_plot_dr_4.setObjectName("lb_plot_dr_4")
        self.horizontalLayout_45.addWidget(self.lb_plot_dr_4)
        self.lb_radar_rmax_12 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_12.setObjectName("lb_radar_rmax_12")
        self.horizontalLayout_45.addWidget(self.lb_radar_rmax_12)
        self.verticalLayout_10.addLayout(self.horizontalLayout_45)
        self.horizontalLayout_46 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_46.setObjectName("horizontalLayout_46")
        self.lb_radar_rmax_13 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_13.setObjectName("lb_radar_rmax_13")
        self.horizontalLayout_46.addWidget(self.lb_radar_rmax_13)
        self.lb_plot_rmax_4 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_plot_rmax_4.setObjectName("lb_plot_rmax_4")
        self.horizontalLayout_46.addWidget(self.lb_plot_rmax_4)
        self.lb_radar_rmax_14 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_14.setObjectName("lb_radar_rmax_14")
        self.horizontalLayout_46.addWidget(self.lb_radar_rmax_14)
        self.verticalLayout_10.addLayout(self.horizontalLayout_46)
        self.horizontalLayout_47 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_47.setObjectName("horizontalLayout_47")
        self.lb_radar_rmax_15 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_15.setObjectName("lb_radar_rmax_15")
        self.horizontalLayout_47.addWidget(self.lb_radar_rmax_15)
        self.lb_plot_rmax_5 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_plot_rmax_5.setObjectName("lb_plot_rmax_5")
        self.horizontalLayout_47.addWidget(self.lb_plot_rmax_5)
        self.lb_radar_rmax_16 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_16.setObjectName("lb_radar_rmax_16")
        self.horizontalLayout_47.addWidget(self.lb_radar_rmax_16)
        self.verticalLayout_10.addLayout(self.horizontalLayout_47)
        self.horizontalLayout_48 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_48.setObjectName("horizontalLayout_48")
        self.lb_radar_rmax_17 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_17.setObjectName("lb_radar_rmax_17")
        self.horizontalLayout_48.addWidget(self.lb_radar_rmax_17)
        self.lb_plot_rmax_6 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_plot_rmax_6.setObjectName("lb_plot_rmax_6")
        self.horizontalLayout_48.addWidget(self.lb_plot_rmax_6)
        self.lb_radar_rmax_18 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_11)
        self.lb_radar_rmax_18.setObjectName("lb_radar_rmax_18")
        self.horizontalLayout_48.addWidget(self.lb_radar_rmax_18)
        self.verticalLayout_10.addLayout(self.horizontalLayout_48)
        self.horizontalLayout_6.addWidget(self.groupBox_6)
        self.sb_switchboard.addTab(self.tab, "")
        self.processing = QtWidgets.QWidget()
        self.processing.setObjectName("processing")
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(parent=self.processing)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(10, 10, 681, 351))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.horizontalLayout_25 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout_25.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_25.setObjectName("horizontalLayout_25")
        self.groupBox_5 = QtWidgets.QGroupBox(parent=self.horizontalLayoutWidget_3)
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayoutWidget_10 = QtWidgets.QWidget(parent=self.groupBox_5)
        self.verticalLayoutWidget_10.setGeometry(QtCore.QRect(10, 40, 321, 301))
        self.verticalLayoutWidget_10.setObjectName("verticalLayoutWidget_10")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_10)
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.horizontalLayout_49 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_49.setObjectName("horizontalLayout_49")
        self.lb_data_processing_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_10)
        self.lb_data_processing_0.setObjectName("lb_data_processing_0")
        self.horizontalLayout_49.addWidget(self.lb_data_processing_0)
        self.verticalLayout_11.addLayout(self.horizontalLayout_49)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.rb_processing_aaft_1 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_10)
        self.rb_processing_aaft_1.setObjectName("rb_processing_aaft_1")
        self.horizontalLayout_11.addWidget(self.rb_processing_aaft_1)
        self.verticalLayout_11.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.rb_processing_arft_rx_1 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_10)
        self.rb_processing_arft_rx_1.setObjectName("rb_processing_arft_rx_1")
        self.horizontalLayout_14.addWidget(self.rb_processing_arft_rx_1)
        self.verticalLayout_11.addLayout(self.horizontalLayout_14)
        self.horizontalLayout_33 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_33.setObjectName("horizontalLayout_33")
        self.rb_processing_arft_rx_2 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_10)
        self.rb_processing_arft_rx_2.setObjectName("rb_processing_arft_rx_2")
        self.horizontalLayout_33.addWidget(self.rb_processing_arft_rx_2)
        self.verticalLayout_11.addLayout(self.horizontalLayout_33)
        self.horizontalLayout_34 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_34.setObjectName("horizontalLayout_34")
        self.rb_processing_arft_rx_3 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_10)
        self.rb_processing_arft_rx_3.setObjectName("rb_processing_arft_rx_3")
        self.horizontalLayout_34.addWidget(self.rb_processing_arft_rx_3)
        self.verticalLayout_11.addLayout(self.horizontalLayout_34)
        self.horizontalLayout_35 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_35.setObjectName("horizontalLayout_35")
        self.rb_processing_arft_rx_4 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_10)
        self.rb_processing_arft_rx_4.setObjectName("rb_processing_arft_rx_4")
        self.horizontalLayout_35.addWidget(self.rb_processing_arft_rx_4)
        self.verticalLayout_11.addLayout(self.horizontalLayout_35)
        spacerItem15 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_11.addItem(spacerItem15)
        self.horizontalLayout_60 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_60.setObjectName("horizontalLayout_60")
        self.lb_signal_peak_set_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_10)
        self.lb_signal_peak_set_1.setObjectName("lb_signal_peak_set_1")
        self.horizontalLayout_60.addWidget(self.lb_signal_peak_set_1)
        self.cb_signal_peak_set_1 = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_10)
        self.cb_signal_peak_set_1.setObjectName("cb_signal_peak_set_1")
        self.horizontalLayout_60.addWidget(self.cb_signal_peak_set_1)
        self.sb_signal_peak_set_1 = QtWidgets.QSpinBox(parent=self.verticalLayoutWidget_10)
        self.sb_signal_peak_set_1.setObjectName("sb_signal_peak_set_1")
        self.horizontalLayout_60.addWidget(self.sb_signal_peak_set_1)
        self.verticalLayout_11.addLayout(self.horizontalLayout_60)
        spacerItem16 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_11.addItem(spacerItem16)
        self.horizontalLayout_52 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_52.setObjectName("horizontalLayout_52")
        self.lb_radar_6 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_10)
        self.lb_radar_6.setObjectName("lb_radar_6")
        self.horizontalLayout_52.addWidget(self.lb_radar_6)
        self.verticalLayout_11.addLayout(self.horizontalLayout_52)
        self.horizontalLayout_55 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_55.setObjectName("horizontalLayout_55")
        self.cb_processing_ai_1 = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_10)
        self.cb_processing_ai_1.setObjectName("cb_processing_ai_1")
        self.horizontalLayout_55.addWidget(self.cb_processing_ai_1)
        self.verticalLayout_11.addLayout(self.horizontalLayout_55)
        self.horizontalLayout_25.addWidget(self.groupBox_5)
        self.groupBox_7 = QtWidgets.QGroupBox(parent=self.horizontalLayoutWidget_3)
        self.groupBox_7.setObjectName("groupBox_7")
        self.verticalLayoutWidget_12 = QtWidgets.QWidget(parent=self.groupBox_7)
        self.verticalLayoutWidget_12.setGeometry(QtCore.QRect(10, 40, 321, 301))
        self.verticalLayoutWidget_12.setObjectName("verticalLayoutWidget_12")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_12)
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.lb_signal_peak_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_signal_peak_0.setObjectName("lb_signal_peak_0")
        self.horizontalLayout_10.addWidget(self.lb_signal_peak_0)
        self.lb_signal_peak_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_signal_peak_1.setObjectName("lb_signal_peak_1")
        self.horizontalLayout_10.addWidget(self.lb_signal_peak_1)
        self.lb_signal_peak_2 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_signal_peak_2.setObjectName("lb_signal_peak_2")
        self.horizontalLayout_10.addWidget(self.lb_signal_peak_2)
        self.verticalLayout_12.addLayout(self.horizontalLayout_10)
        spacerItem17 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_12.addItem(spacerItem17)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.lb_radar_rr_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_radar_rr_0.setObjectName("lb_radar_rr_0")
        self.horizontalLayout_4.addWidget(self.lb_radar_rr_0)
        self.lb_radar_rr_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_radar_rr_1.setObjectName("lb_radar_rr_1")
        self.horizontalLayout_4.addWidget(self.lb_radar_rr_1)
        self.lb_radar_rr_2 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_radar_rr_2.setObjectName("lb_radar_rr_2")
        self.horizontalLayout_4.addWidget(self.lb_radar_rr_2)
        self.verticalLayout_12.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.lb_radar_hr_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_radar_hr_0.setObjectName("lb_radar_hr_0")
        self.horizontalLayout_5.addWidget(self.lb_radar_hr_0)
        self.lb_radar_hr_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_radar_hr_1.setObjectName("lb_radar_hr_1")
        self.horizontalLayout_5.addWidget(self.lb_radar_hr_1)
        self.lb_radar_hr_2 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_radar_hr_2.setObjectName("lb_radar_hr_2")
        self.horizontalLayout_5.addWidget(self.lb_radar_hr_2)
        self.verticalLayout_12.addLayout(self.horizontalLayout_5)
        spacerItem18 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_12.addItem(spacerItem18)
        self.horizontalLayout_37 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_37.setObjectName("horizontalLayout_37")
        self.lb_ai_rr_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_ai_rr_0.setLineWidth(1)
        self.lb_ai_rr_0.setObjectName("lb_ai_rr_0")
        self.horizontalLayout_37.addWidget(self.lb_ai_rr_0)
        self.lb_ai_rr_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_ai_rr_1.setObjectName("lb_ai_rr_1")
        self.horizontalLayout_37.addWidget(self.lb_ai_rr_1)
        self.lb_ai_rr_2 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_ai_rr_2.setObjectName("lb_ai_rr_2")
        self.horizontalLayout_37.addWidget(self.lb_ai_rr_2)
        self.verticalLayout_12.addLayout(self.horizontalLayout_37)
        self.horizontalLayout_36 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_36.setObjectName("horizontalLayout_36")
        self.lb_ai_hr_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_ai_hr_0.setObjectName("lb_ai_hr_0")
        self.horizontalLayout_36.addWidget(self.lb_ai_hr_0)
        self.lb_ai_hr_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_ai_hr_1.setObjectName("lb_ai_hr_1")
        self.horizontalLayout_36.addWidget(self.lb_ai_hr_1)
        self.lb_ai_hr_2 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_ai_hr_2.setObjectName("lb_ai_hr_2")
        self.horizontalLayout_36.addWidget(self.lb_ai_hr_2)
        self.verticalLayout_12.addLayout(self.horizontalLayout_36)
        spacerItem19 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_12.addItem(spacerItem19)
        self.horizontalLayout_38 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_38.setObjectName("horizontalLayout_38")
        self.lb_uart_rr_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_uart_rr_0.setObjectName("lb_uart_rr_0")
        self.horizontalLayout_38.addWidget(self.lb_uart_rr_0)
        self.lb_uart_rr_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_uart_rr_1.setObjectName("lb_uart_rr_1")
        self.horizontalLayout_38.addWidget(self.lb_uart_rr_1)
        self.lb_uart_rr_2 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_uart_rr_2.setObjectName("lb_uart_rr_2")
        self.horizontalLayout_38.addWidget(self.lb_uart_rr_2)
        self.verticalLayout_12.addLayout(self.horizontalLayout_38)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.lb_uart_hr_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_uart_hr_0.setObjectName("lb_uart_hr_0")
        self.horizontalLayout_7.addWidget(self.lb_uart_hr_0)
        self.lb_uart_hr_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_uart_hr_1.setObjectName("lb_uart_hr_1")
        self.horizontalLayout_7.addWidget(self.lb_uart_hr_1)
        self.lb_uart_hr_2 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.lb_uart_hr_2.setObjectName("lb_uart_hr_2")
        self.horizontalLayout_7.addWidget(self.lb_uart_hr_2)
        self.verticalLayout_12.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_25.addWidget(self.groupBox_7)
        self.sb_switchboard.addTab(self.processing, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayoutWidget_4 = QtWidgets.QWidget(parent=self.tab_2)
        self.horizontalLayoutWidget_4.setGeometry(QtCore.QRect(10, 10, 681, 351))
        self.horizontalLayoutWidget_4.setObjectName("horizontalLayoutWidget_4")
        self.horizontalLayout_26 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_4)
        self.horizontalLayout_26.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_26.setObjectName("horizontalLayout_26")
        self.groupBox_8 = QtWidgets.QGroupBox(parent=self.horizontalLayoutWidget_4)
        self.groupBox_8.setObjectName("groupBox_8")
        self.verticalLayoutWidget_13 = QtWidgets.QWidget(parent=self.groupBox_8)
        self.verticalLayoutWidget_13.setGeometry(QtCore.QRect(10, 40, 321, 301))
        self.verticalLayoutWidget_13.setObjectName("verticalLayoutWidget_13")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_13)
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.rb_plot_aaft_1 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_13)
        self.rb_plot_aaft_1.setObjectName("rb_plot_aaft_1")
        self.horizontalLayout_13.addWidget(self.rb_plot_aaft_1)
        self.verticalLayout_13.addLayout(self.horizontalLayout_13)
        spacerItem20 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_13.addItem(spacerItem20)
        self.horizontalLayout_31 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_31.setObjectName("horizontalLayout_31")
        self.rb_plot_arft_1 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_13)
        self.rb_plot_arft_1.setObjectName("rb_plot_arft_1")
        self.horizontalLayout_31.addWidget(self.rb_plot_arft_1)
        self.verticalLayout_13.addLayout(self.horizontalLayout_31)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.cb_plot_arft_rx_1 = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_13)
        self.cb_plot_arft_rx_1.setObjectName("cb_plot_arft_rx_1")
        self.horizontalLayout_3.addWidget(self.cb_plot_arft_rx_1)
        self.cb_plot_arft_rx_2 = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_13)
        self.cb_plot_arft_rx_2.setObjectName("cb_plot_arft_rx_2")
        self.horizontalLayout_3.addWidget(self.cb_plot_arft_rx_2)
        self.cb_plot_arft_rx_3 = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_13)
        self.cb_plot_arft_rx_3.setObjectName("cb_plot_arft_rx_3")
        self.horizontalLayout_3.addWidget(self.cb_plot_arft_rx_3)
        self.cb_plot_arft_rx_4 = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_13)
        self.cb_plot_arft_rx_4.setObjectName("cb_plot_arft_rx_4")
        self.horizontalLayout_3.addWidget(self.cb_plot_arft_rx_4)
        self.verticalLayout_13.addLayout(self.horizontalLayout_3)
        spacerItem21 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_13.addItem(spacerItem21)
        self.horizontalLayout_30 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_30.setObjectName("horizontalLayout_30")
        self.rb_plot_signal_1 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_13)
        self.rb_plot_signal_1.setObjectName("rb_plot_signal_1")
        self.horizontalLayout_30.addWidget(self.rb_plot_signal_1)
        self.verticalLayout_13.addLayout(self.horizontalLayout_30)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.cb_plot_phase_signal_1 = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_13)
        self.cb_plot_phase_signal_1.setObjectName("cb_plot_phase_signal_1")
        self.horizontalLayout_12.addWidget(self.cb_plot_phase_signal_1)
        self.cb_plot_heart_signal_1 = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_13)
        self.cb_plot_heart_signal_1.setObjectName("cb_plot_heart_signal_1")
        self.horizontalLayout_12.addWidget(self.cb_plot_heart_signal_1)
        self.cb_plot_breath_signal_1 = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_13)
        self.cb_plot_breath_signal_1.setObjectName("cb_plot_breath_signal_1")
        self.horizontalLayout_12.addWidget(self.cb_plot_breath_signal_1)
        self.verticalLayout_13.addLayout(self.horizontalLayout_12)
        spacerItem22 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_13.addItem(spacerItem22)
        self.horizontalLayout_26.addWidget(self.groupBox_8)
        self.groupBox_9 = QtWidgets.QGroupBox(parent=self.horizontalLayoutWidget_4)
        self.groupBox_9.setObjectName("groupBox_9")
        self.verticalLayoutWidget_14 = QtWidgets.QWidget(parent=self.groupBox_9)
        self.verticalLayoutWidget_14.setGeometry(QtCore.QRect(10, 40, 321, 301))
        self.verticalLayoutWidget_14.setObjectName("verticalLayoutWidget_14")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_14)
        self.verticalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.horizontalLayout_29 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_29.setObjectName("horizontalLayout_29")
        self.lb_plot_frame_rate_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_14)
        self.lb_plot_frame_rate_1.setObjectName("lb_plot_frame_rate_1")
        self.horizontalLayout_29.addWidget(self.lb_plot_frame_rate_1)
        self.lb_plot_frame_rate_2 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_14)
        self.lb_plot_frame_rate_2.setObjectName("lb_plot_frame_rate_2")
        self.horizontalLayout_29.addWidget(self.lb_plot_frame_rate_2)
        self.verticalLayout_14.addLayout(self.horizontalLayout_29)
        spacerItem23 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_14.addItem(spacerItem23)
        self.horizontalLayout_26.addWidget(self.groupBox_9)
        self.sb_switchboard.addTab(self.tab_2, "")
        self.record_data = QtWidgets.QWidget()
        self.record_data.setObjectName("record_data")
        self.horizontalLayoutWidget_5 = QtWidgets.QWidget(parent=self.record_data)
        self.horizontalLayoutWidget_5.setGeometry(QtCore.QRect(10, 10, 681, 351))
        self.horizontalLayoutWidget_5.setObjectName("horizontalLayoutWidget_5")
        self.horizontalLayout_27 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_5)
        self.horizontalLayout_27.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_27.setObjectName("horizontalLayout_27")
        self.groupBox_10 = QtWidgets.QGroupBox(parent=self.horizontalLayoutWidget_5)
        self.groupBox_10.setObjectName("groupBox_10")
        self.verticalLayoutWidget_15 = QtWidgets.QWidget(parent=self.groupBox_10)
        self.verticalLayoutWidget_15.setGeometry(QtCore.QRect(10, 40, 321, 301))
        self.verticalLayoutWidget_15.setObjectName("verticalLayoutWidget_15")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_15)
        self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.btn_record_start_1 = QtWidgets.QPushButton(parent=self.verticalLayoutWidget_15)
        self.btn_record_start_1.setObjectName("btn_record_start_1")
        self.horizontalLayout_8.addWidget(self.btn_record_start_1)
        self.btn_record_stop_1 = QtWidgets.QPushButton(parent=self.verticalLayoutWidget_15)
        self.btn_record_stop_1.setObjectName("btn_record_stop_1")
        self.horizontalLayout_8.addWidget(self.btn_record_stop_1)
        self.verticalLayout_15.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_28 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_28.setObjectName("horizontalLayout_28")
        self.lb_record_count_0 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_15)
        self.lb_record_count_0.setObjectName("lb_record_count_0")
        self.horizontalLayout_28.addWidget(self.lb_record_count_0)
        self.lb_record_count_1 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_15)
        self.lb_record_count_1.setObjectName("lb_record_count_1")
        self.horizontalLayout_28.addWidget(self.lb_record_count_1)
        self.verticalLayout_15.addLayout(self.horizontalLayout_28)
        spacerItem24 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_15.addItem(spacerItem24)
        self.horizontalLayout_27.addWidget(self.groupBox_10)
        self.groupBox_11 = QtWidgets.QGroupBox(parent=self.horizontalLayoutWidget_5)
        self.groupBox_11.setObjectName("groupBox_11")
        self.verticalLayoutWidget_16 = QtWidgets.QWidget(parent=self.groupBox_11)
        self.verticalLayoutWidget_16.setGeometry(QtCore.QRect(10, 40, 321, 301))
        self.verticalLayoutWidget_16.setObjectName("verticalLayoutWidget_16")
        self.verticalLayout_16 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_16)
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.horizontalLayout_32 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_32.setObjectName("horizontalLayout_32")
        self.lb_radar_8 = QtWidgets.QLabel(parent=self.verticalLayoutWidget_16)
        self.lb_radar_8.setObjectName("lb_radar_8")
        self.horizontalLayout_32.addWidget(self.lb_radar_8)
        self.verticalLayout_16.addLayout(self.horizontalLayout_32)
        spacerItem25 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_16.addItem(spacerItem25)
        self.horizontalLayout_27.addWidget(self.groupBox_11)
        self.sb_switchboard.addTab(self.record_data, "")
        self.gridLayout.addWidget(self.sb_switchboard, 1, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 757, 22))
        self.menubar.setObjectName("menubar")
        self.menuStart = QtWidgets.QMenu(parent=self.menubar)
        self.menuStart.setObjectName("menuStart")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.actionClose = QtGui.QAction(parent=self)
        self.actionClose.setCheckable(True)
        self.actionClose.setChecked(True)
        self.actionClose.setObjectName("actionClose")
        self.menuStart.addAction(self.actionClose)
        self.menubar.addAction(self.menuStart.menuAction())


        self.gui_retranslate_ui()
        self.gui_plot_initialization()

        self.sb_switchboard.setCurrentIndex(0)
        self.cbb_device_uart_settings_1.setCurrentIndex(0)
        self.cbb_radar_settings_1.setCurrentIndex(0)
        
        self.actionClose.triggered.connect(self.update) 
        self.cb_data_aaft_1.stateChanged.connect(self.gui_cb_communication_aaft_1) 
        self.cb_data_arft_1.stateChanged.connect(self.gui_cb_communication_arft_1) 
        self.btn_radar_connect_1.clicked.connect(self.gui_btn_radar_connect) 
        self.btn_record_start_1.clicked.connect(self.gui_btn_record_start_1) 
        self.btn_radar_disconnect_1.clicked.connect(self.gui_btn_radar_disconnect) 
        self.btn_device_uart_connect_1.clicked.connect(self.gui_btn_uart_connect) 
        self.btn_device_uart_disconnect_1.clicked.connect(self.gui_btn_uart_disconnect) 
        self.btn_record_stop_1.clicked.connect(self.gui_btn_record_stop_1) 
        self.cb_plot_arft_rx_1.stateChanged.connect(self.gui_cb_plot_arft_rx_1) 
        self.cb_plot_arft_rx_2.stateChanged.connect(self.gui_cb_plot_arft_rx_2) 
        self.cb_plot_arft_rx_3.stateChanged.connect(self.gui_cb_plot_arft_rx_3) 
        self.cb_plot_arft_rx_4.stateChanged.connect(self.gui_cb_plot_arft_rx_4) 
        self.cb_plot_breath_signal_1.stateChanged.connect(self.gui_cb_breath_signal_1_changed) 
        self.cb_plot_heart_signal_1.stateChanged.connect(self.gui_cb_heart_signal_1_changed) 
        self.cb_plot_phase_signal_1.stateChanged.connect(self.gui_cb_phase_signal_1_changed) 
        self.rb_plot_aaft_1.clicked.connect(self.gui_rb_aaft_plot) 
        self.rb_plot_arft_1.clicked.connect(self.gui_rb_arft_plot) 
        self.rb_plot_signal_1.clicked.connect(self.gui_rb_signal_plot) 
        self.rb_processing_aaft_1.clicked.connect(self.gui_rb_processing_aaft_1) 
        self.rb_processing_arft_rx_1.clicked.connect(self.gui_rb_processing_arft_rx_1) 
        self.rb_processing_arft_rx_2.clicked.connect(self.gui_rb_processing_arft_rx_2) 
        self.rb_processing_arft_rx_3.clicked.connect(self.gui_rb_processing_arft_rx_3) 
        self.rb_processing_arft_rx_4.clicked.connect(self.gui_rb_processing_arft_rx_4) 
        self.cbb_radar_settings_1.activated.connect(self.cbb_radar_settings_1.update) 
        self.cb_processing_ai_1.stateChanged.connect(self.gui_cb_processing_ai_1)
        self.cb_signal_peak_set_1.stateChanged.connect(self.gui_cb_signal_peak_set_1) 
        self.cbb_device_uart_settings_1.activated.connect(self.cbb_device_uart_settings_1.update)
        QtCore.QMetaObject.connectSlotsByName(self)
        


    def gui_plot_initialization(self):
    
        self.graphicsView.showGrid(x=True, y=True, alpha=0.4)
        
        self.graphicsView.setLabel('left', 'Amplitude', units='E')
        self.graphicsView.setLabel('bottom', 'Distance', units='m')
        
        self.x_frame = np.linspace(0, 12.8, SAMPLES)
        self.y_frame = np.linspace(0, 0, SAMPLES)
        
        self.x_signal = np.linspace(0, SWEEPS // 100, SWEEPS)
        self.y_signal = np.linspace(0, 0, SWEEPS)
        
        self.graphicsView.setBackground('w')

        self.plot1 = self.graphicsView.plot(self.x_frame, self.y_frame, pen='r')
        self.plot2 = self.graphicsView.plot(self.x_frame, self.y_frame, pen='g')
        self.plot3 = self.graphicsView.plot(self.x_frame, self.y_frame, pen='b')
        self.plot4 = self.graphicsView.plot(self.x_frame, self.y_frame, pen='y')
        
        self.legend = LegendItem(offset=(0, 0))
        self.legend.setParentItem(self.graphicsView.plotItem)
        self.legend.anchor(itemPos=(1, 0), parentPos=(1, 0), offset=(-10, 10))

    def gui_retranslate_ui(self):
    
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("self", "CTP - Vital Signs"))
        self.groupBox.setTitle(_translate("self", "Device"))
        self.lb_device_radar_0.setText(_translate("self", "Radar"))
        self.btn_radar_connect_1.setText(_translate("self", "Connect"))
        self.btn_radar_disconnect_1.setText(_translate("self", "Disconnect"))
        self.lb_radar_ip_udp_0.setText(_translate("self", "Server IP"))
        self.lb_radar_ip_udp_1.setText(_translate("self", "192.168.100.201"))
        self.lb_radar_ip_tcp_0.setText(_translate("self", "Client IP"))
        self.lb_radar_ip_tcp_1.setText(_translate("self", "192.168.100.1"))
        self.lb_device_chest_strap_0.setText(_translate("self", "UART"))
        self.btn_device_uart_connect_1.setText(_translate("self", "Connect"))
        self.btn_device_uart_disconnect_1.setText(_translate("self", "Disconnect"))
        self.cbb_device_uart_settings_1.setCurrentText(_translate("self", "00:35:FF:2F:20:AB"))
        self.cbb_device_uart_settings_1.setItemText(0, _translate("self", "00:35:FF:2F:20:AB"))
        self.groupBox_2.setTitle(_translate("self", "Info"))
        self.lb_info_radar_0.setText(_translate("self", "Radar"))
        self.lb_info_radar_server_0.setText(_translate("self", "Server"))
        self.lb_info_radar_server_1.setText(_translate("self", "_"))
        self.lb_info_radar_client_0.setText(_translate("self", "Client"))
        self.lb_info_radar_client_1.setText(_translate("self", "_"))
        self.lb_info_radar_firmware_0.setText(_translate("self", "Firmware"))
        self.lb_info_radar_firmware_1.setText(_translate("self", "_"))
        self.lb_info_radar_fpga_0.setText(_translate("self", "FPGA"))
        self.lb_info_radar_fpga_1.setText(_translate("self", "_"))
        self.lb_info_chest_strap_0.setText(_translate("self", "UART"))
        self.lb_info_chest_strap_manufacturer_0.setText(_translate("self", "Device Name"))
        self.lb_info_polar_manufacturer_1.setText(_translate("self", "_"))
        self.lb_info_chest_strap_model_0.setText(_translate("self", "Appearance"))
        self.lb_info_polar_model_1.setText(_translate("self", "_"))
        self.lb_info_chest_strap_serial_0.setText(_translate("self", "Serial"))
        self.lb_info_polar_serial_1.setText(_translate("self", "_"))
        self.groupBox_3.setTitle(_translate("self", "Data Output"))
        self.lb_data_radar_0.setText(_translate("self", "Radar"))
        self.cb_data_arft_1.setText(_translate("self", "ARFT"))
        self.cb_data_aaft_1.setText(_translate("self", "AAFT"))
        self.sb_switchboard.setTabText(self.sb_switchboard.indexOf(self.communication), _translate("self", "Communication"))
        self.groupBox_4.setTitle(_translate("self", "Settings"))
        self.cbb_radar_settings_1.setCurrentText(_translate("self", "#1 12.8m, 256/4 100Hz, TX1"))
        self.cbb_radar_settings_1.setItemText(0, _translate("self", "#1 12.8m, 256/4 100Hz, TX1"))
        self.cbb_radar_settings_1.setItemText(1, _translate("self", "#2 12.8m, 256/4 100Hz, TX1&3"))
        self.cbb_radar_settings_1.setItemText(2, _translate("self", "#3 12.8m, 256/4 100Hz, TX1&2&3"))
        self.cbb_radar_settings_1.setItemText(3, _translate("self", "#4 12.8m, 256/16 50Hz, TX1&3"))
        self.cbb_radar_settings_1.setItemText(4, _translate("self", "#5 12.8m, 256/32 25Hz, TX1&3"))
        self.groupBox_6.setTitle(_translate("self", "Info"))
        self.lb_radar_rmax_3.setText(_translate("self", "Samples"))
        self.lineEdit_3.setText(_translate("self", "256"))
        self.lb_radar_rmax_6.setText(_translate("self", "[E]"))
        self.lb_radar_rmax_21.setText(_translate("self", "Sample rate"))
        self.lineEdit_8.setText(_translate("self", "4000000"))
        self.lb_radar_rmax_22.setText(_translate("self", "[sps]"))
        self.lb_radar_rmax_4.setText(_translate("self", "Frame rate"))
        self.lineEdit_4.setText(_translate("self", "100"))
        self.lb_radar_rmax_7.setText(_translate("self", "[Hz]"))
        self.lb_radar_rmax_5.setText(_translate("self", "Carrier Frequency"))
        self.lineEdit_5.setText(_translate("self", "61000000000"))
        self.lb_radar_rmax_8.setText(_translate("self", "[Hz]"))
        self.lb_plot_rmax_1.setText(_translate("self", "Distance"))
        self.lineEdit_6.setText(_translate("self", "12.8"))
        self.lb_radar_rmax_11.setText(_translate("self", "[m]"))
        self.lb_radar_rmax_9.setText(_translate("self", "Wavelength"))
        self.lb_plot_rmax_3.setText(_translate("self", "_"))
        self.lb_radar_rmax_10.setText(_translate("self", "[m]"))
        self.lb_plot_dr_3.setText(_translate("self", "d_R"))
        self.lb_plot_dr_4.setText(_translate("self", "_"))
        self.lb_radar_rmax_12.setText(_translate("self", "[(m)]"))
        self.lb_radar_rmax_13.setText(_translate("self", "Bandwidth"))
        self.lb_plot_rmax_4.setText(_translate("self", "_"))
        self.lb_radar_rmax_14.setText(_translate("self", "[Hz]"))
        self.lb_radar_rmax_15.setText(_translate("self", "Sampling time"))
        self.lb_plot_rmax_5.setText(_translate("self", "_"))
        self.lb_radar_rmax_16.setText(_translate("self", "[s]"))
        self.lb_radar_rmax_17.setText(_translate("self", "Slope"))
        self.lb_plot_rmax_6.setText(_translate("self", "_"))
        self.lb_radar_rmax_18.setText(_translate("self", "[Hz]"))
        self.sb_switchboard.setTabText(self.sb_switchboard.indexOf(self.tab), _translate("self", "Radar"))
        self.groupBox_5.setTitle(_translate("self", "Settings"))
        self.lb_data_processing_0.setText(_translate("self", "Classic data processing"))
        self.rb_processing_aaft_1.setText(_translate("self", "AAFT"))
        self.rb_processing_arft_rx_1.setText(_translate("self", "ARFT_RX_1"))
        self.rb_processing_arft_rx_2.setText(_translate("self", "ARFT_RX_2"))
        self.rb_processing_arft_rx_3.setText(_translate("self", "ARFT_RX_3"))
        self.rb_processing_arft_rx_4.setText(_translate("self", "ARFT_RX_4"))
        self.lb_signal_peak_set_1.setText(_translate("self", "Set Signal Peak"))
        self.cb_signal_peak_set_1.setText(_translate("self", "Enable"))
        self.lb_radar_6.setText(_translate("self", "Artificial intelligence and data processing"))
        self.cb_processing_ai_1.setText(_translate("self", "AI"))
        self.groupBox_7.setTitle(_translate("self", "Measurement"))
        self.lb_signal_peak_0.setText(_translate("self", "Signal"))
        self.lb_signal_peak_1.setText(_translate("self", "peak"))
        self.lb_signal_peak_2.setText(_translate("self", "0"))
        self.lb_radar_rr_0.setText(_translate("self", "Radar"))
        self.lb_radar_rr_1.setText(_translate("self", "respiratory_rate"))
        self.lb_radar_rr_2.setText(_translate("self", "0"))
        self.lb_radar_hr_0.setText(_translate("self", "Radar"))
        self.lb_radar_hr_1.setText(_translate("self", "heart_rate"))
        self.lb_radar_hr_2.setText(_translate("self", "0"))
        self.lb_ai_rr_0.setText(_translate("self", "AI"))
        self.lb_ai_rr_1.setText(_translate("self", "respiratory_rate"))
        self.lb_ai_rr_2.setText(_translate("self", "0"))
        self.lb_ai_hr_0.setText(_translate("self", "AI"))
        self.lb_ai_hr_1.setText(_translate("self", "heart_rate"))
        self.lb_ai_hr_2.setText(_translate("self", "0"))
        self.lb_uart_rr_0.setText(_translate("self", "UART"))
        self.lb_uart_rr_1.setText(_translate("self", "respiratory_rate"))
        self.lb_uart_rr_2.setText(_translate("self", "0"))
        self.lb_uart_hr_0.setText(_translate("self", "UART"))
        self.lb_uart_hr_1.setText(_translate("self", "heart_rate"))
        self.lb_uart_hr_2.setText(_translate("self", "0"))
        self.sb_switchboard.setTabText(self.sb_switchboard.indexOf(self.processing), _translate("self", "Processing"))
        self.groupBox_8.setTitle(_translate("self", "Settings"))
        self.rb_plot_aaft_1.setText(_translate("self", "AAFT"))
        self.rb_plot_arft_1.setText(_translate("self", "ARFT"))
        self.cb_plot_arft_rx_1.setText(_translate("self", "RX_1"))
        self.cb_plot_arft_rx_2.setText(_translate("self", "RX_2"))
        self.cb_plot_arft_rx_3.setText(_translate("self", "RX_3"))
        self.cb_plot_arft_rx_4.setText(_translate("self", "RX_4"))
        self.rb_plot_signal_1.setText(_translate("self", "Signal"))
        self.cb_plot_phase_signal_1.setText(_translate("self", "Phase Signal"))
        self.cb_plot_heart_signal_1.setText(_translate("self", "Heart Signal"))
        self.cb_plot_breath_signal_1.setText(_translate("self", "Breath Signal"))
        self.groupBox_9.setTitle(_translate("self", "Data"))
        self.lb_plot_frame_rate_1.setText(_translate("self", "Frame rate"))
        self.lb_plot_frame_rate_2.setText(_translate("self", "0"))
        self.sb_switchboard.setTabText(self.sb_switchboard.indexOf(self.tab_2), _translate("self", "Plot"))
        self.groupBox_10.setTitle(_translate("self", "Record"))
        self.btn_record_start_1.setText(_translate("self", "Start"))
        self.btn_record_stop_1.setText(_translate("self", "Stop"))
        self.lb_record_count_0.setText(_translate("self", "Count"))
        self.lb_record_count_1.setText(_translate("self", "0"))
        self.groupBox_11.setTitle(_translate("self", "Playback"))
        self.lb_radar_8.setText(_translate("self", "_"))
        self.sb_switchboard.setTabText(self.sb_switchboard.indexOf(self.record_data), _translate("self", "Record"))
        self.menuStart.setTitle(_translate("self", "Start"))
        self.actionClose.setText(_translate("self", "Close"))