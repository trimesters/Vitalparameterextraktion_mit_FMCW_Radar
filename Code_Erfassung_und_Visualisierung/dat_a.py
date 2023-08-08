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


class Pulse_Respiration_CNN(nn.Module):
    
    def __init__(self, 
                 input_width, 
                 conv_layer_, 
                 fc_layers_, 
                 conv_channel_, 
                 conv_kernel_, 
                 conv_stride_,
                 pool_kernel_, 
                 pool_stride_,
                 fully_connected_):
        
        super(Pulse_Respiration_CNN, self).__init__()

        self.af_1 = nn.Tanh()
        self.af_2 = nn.ReLU()

        self.conv_1_layers = nn.ModuleList()
        self.bn_1_layers = nn.ModuleList()
        self.pool_1_layers = nn.ModuleList()
        
        self.fc_layers = nn.ModuleList()
        
        conv_layer = conv_layer_
        fc_layers = fc_layers_
        
        print(f"conv_layer: {conv_layer}")
        print(f"fc_layers: {fc_layers}")

        Width = input_width
        in_channels = 1

        for i in range(conv_layer):
            
            conv_channel = conv_channel_[i]
            conv_kernel = conv_kernel_[i]
            conv_stride = conv_stride_[i]
            
            pool_kernel = pool_kernel_[i]
            pool_stride = pool_stride_[i]
     
            Kernel = conv_kernel # kernel_size
            Padding = 0 # (Kernel - 1) // 2 # padding
            Stride = conv_stride # stride
            Width_a = ((Width - conv_kernel + 2 * Padding) // conv_stride) + 1
            
            Width_b = ((Width_a - pool_kernel) // pool_stride) + 1
            
            if (Width_b < 4):
                Kernel = conv_kernel * conv_stride + pool_kernel * pool_stride
            
                Padding = (Kernel - 1) // 2 # padding
                Width = ((Width - conv_kernel + 2 * Padding) // conv_stride) + 1
                Width = ((Width - pool_kernel) // pool_stride) + 1
            else:
                Width = Width_b
            
            self.conv_1_layers.append(nn.Conv1d(in_channels=in_channels, out_channels=conv_channel, kernel_size=conv_kernel, stride=conv_stride, padding=Padding))
            self.bn_1_layers.append(nn.BatchNorm1d(conv_channel))
            self.pool_1_layers.append(nn.MaxPool1d(pool_kernel, pool_stride)) 
            in_channels = conv_channel
            
            print(f"s{i}_conv_channel_1: {conv_channel} s{i}_conv_kernel_1: {conv_kernel} s{i}_conv_stride_1: {conv_stride} s{i}_padding_1: {Padding} s{i}_pool_kernel_1: {pool_kernel} s{i}_pool_stride_1: {pool_stride} s{i}_Width_1: {Width}")
        
        out_features = Width * in_channels
        
        print(f"s{i}_features: {out_features} = Width: {Width} * in_channels: {in_channels}")

        for i in range(fc_layers):
            
            out_features_next = fully_connected_[i]
            self.fc_layers.append(nn.Linear(in_features=out_features, out_features=out_features_next))
            out_features = out_features_next
            
            print(f"s{i}_fully_connected_: {out_features_next}")
            
        self.fc_out = nn.Linear(in_features=out_features, out_features=1)    
        
    def forward(self, x):

        for conv_1, bn_1, pool_1 in zip(self.conv_1_layers, self.bn_1_layers, self.pool_1_layers):
            
            x = conv_1(x)
            x = bn_1(x)
            x = self.af_1(x)
            x = pool_1(x)

        x = x.view(x.size(0), -1)
        
        for layer_1 in self.fc_layers:
            
            x = layer_1(x)
            x = self.af_2(x)
            
        x = self.fc_out(x)
        
        return x
    
class Artificial_Intelligence: 
        
    def __init__(self, 
                 mediator_: mea.Mediator = None
                ):

        self.mediator = mediator_
        
        self.is_radar_connected = False
        self.is_pulsoximeter_connected = False

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        
        self.ai_open_model(True) # TODO: Besserer ort

    def ai_open_model(self, is_connected):

        conv_layer = 8
        fc_layers = 2

        conv_channel = [16,16,16,32,16,64,32,16]
        conv_kernel = [5,29,3,29,3,29,7,17]
        pool_kernel = [5,5,3,4,4,3,4,5]
        pool_stride = [2,1,1,1,1,1,1,1]

        fully_connected = [32,32]

        self.model = Pulse_Respiration_CNN(input_width = input_s_, 
                                      conv_layer_ = conv_layer, 
                                      fc_layers_ = fc_layers, 
                                      conv_channel_ = conv_channel, 
                                      conv_kernel_ = conv_kernel, 
                                      pool_kernel_ = pool_kernel, 
                                      pool_stride_ = pool_stride,
                                      fully_connected_ = fully_connected).to(device)

        dateipfad = "1d_cnn_model_test.pt"

        if os.path.isfile(dateipfad):
            print("Die Datei existiert.")
            model.load_state_dict(torch.load(model_name))
            
        self.model.eval() 
        
    def ai_get_prediction(self, data):
        
        pt_data_1d = torch.tensor(data).float().to(self.device)
        
        pt_data_2d = torch.unsqueeze(pt_data_1d, 0)

        pt_data_3d = torch.unsqueeze(pt_data_2d, 2)

        with torch.no_grad():
            self.prediction = self.model(pt_data_3d)
            
        self.mediator.exchange_data(self, "ai_prediction", self.prediction.cpu().detach().numpy())
                