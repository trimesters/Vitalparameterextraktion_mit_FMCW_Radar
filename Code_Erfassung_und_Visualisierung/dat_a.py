"""
/**************************************************************************************************
 *
 *  @file       dat_a.py
 *  @brief      Artificial_Intelligence
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

import torch
import torch.nn as nn
import torch.optim as optim

# project libraries
import med_a as mea

from dat_d import *

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


class LSTM_Model(nn.Module):
    
    def __init__(self, input_size, hidden_size, num_layers, output_size, device):
        
        super(LSTM_Model, self).__init__()
        
        self.device = device
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(self.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(self.device)
        
        out, _ = self.lstm(x, (h0, c0))
        out = out[:, -1, :]
        out = self.fc(out)
        
        return out

    
class Artificial_Intelligence: 
        
    def __init__(self, 
                 mediator_: mea.Mediator = None
                ):

        self.mediator = mediator_
        
        self.is_running = True
        
        self.is_radar_connected = False
        self.is_pulsoximeter_connected = False
        
        
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        
        self.ai_open_model(True) # TODO: Besserer ort

    def ai_open_model(self, is_connected):

        input_size = 1
        hidden_size = 64
        num_layers = 2
        output_size = 2

        self.model = LSTM_Model(input_size, hidden_size, num_layers, output_size, self.device).to(self.device)

        self.model.load_state_dict(torch.load("lstm_model.pt"))
        self.model.eval() 
        
    def ai_get_prediction(self, data):
        
        pt_data_1d = torch.tensor(data).float().to(self.device)
        
        pt_data_2d = torch.unsqueeze(pt_data_1d, 0)

        pt_data_3d = torch.unsqueeze(pt_data_2d, 2)

        with torch.no_grad():
            self.prediction = self.model(pt_data_3d)
            
        self.mediator.exchange_data(self, "ai_prediction", self.prediction.cpu().detach().numpy())
                