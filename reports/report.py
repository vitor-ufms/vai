#!/usr/bin/env python3

"""     Main app for graphics reports   """
import argparse
from math import log2
import sys
import socket
import random
import getopt

import os

import time
import json


import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import numpy as np
import csv
import pywt

from scapy.all import sniff, rdpcap
from scapy.all import sendp
from scapy.all import get_if_list, get_if_hwaddr

from includes import plotter, wavelet, loader


#* ********************** CONSTANT VALUES ****************** *#
LEVEL_NAME = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
JSON_CONFIG_FILENAME = '../conf.json'


#* ********************** GLOBAL VARIABLES ****************** *#
def set_var_global():
    with open(JSON_CONFIG_FILENAME) as json_file:
        data = json.load(json_file)

    global PCAP_DIR        
    global PCAP_FILENAME   
    global TEST_DIR        
    global REPORT_DIR        
    global TEST_PREFIX     

    global NUMBER_LEVELS   
    global SIZE_BIT        
    global PADDING         
    global SIZE_COUNT
    global DELAY     
    global SIZE_CHUNCK 

    global TEST_DIR_PATH
    global REPORT_DIR_PATH

    global NUMBER_PLOTS

    global PCAP_SIGNAL
    
    global SNR_DATA

    PCAP_DIR        = data["directories"]["PCAP_DIR"]
    PCAP_FILENAME   = data["directories"]["PCAP_DIR"] + data["filenames"]["PCAP_FILENAME"]
    TEST_DIR        = data["directories"]["TEST_DIR"]
    REPORT_DIR      = data["directories"]["REPORT_DIR"]
    TEST_PREFIX     = data["filenames"]["TEST_PREFIX"]

    NUMBER_LEVELS   = data["configuration"]["NUM_LEVELS"]
    SIZE_BIT        = data["configuration"]["SIZE_BIT"]
    PADDING         = data["configuration"]["PADDING"]
    SIZE_COUNT      = data["configuration"]["SIZE_COUNT"]

    TEST_DIR_PATH =  TEST_DIR + TEST_PREFIX + "/"
    REPORT_DIR_PATH =  REPORT_DIR + TEST_PREFIX + "/"

    DELAY = 0
    PCAP_SIGNAL, SIZE_CHUNCK= loader.get_signal_from_pcap(PCAP_FILENAME, DELAY, PADDING, SIZE_COUNT)
    SIZE_CHUNCK = 300
    PCAP_SIGNAL = PCAP_SIGNAL[:SIZE_CHUNCK]

    NUMBER_PLOTS    = NUMBER_LEVELS + 1

    SNR_DATA   = data["snr_test_complete"]


    print(PCAP_FILENAME)
    print(TEST_DIR)
    print(TEST_PREFIX)
    print(NUMBER_LEVELS)
    print(SIZE_BIT)
    print(PADDING)
    print(SIZE_COUNT)
    print(SIZE_CHUNCK)


def get_py_dwt(signal, size_signals, number_levels, type_coeff = "lp"):
    dwt_levels = list()
    dwt = wavelet.extract_dwt_coeffs (signal, 'db1', number_levels, type_coeff)
    for i, size in enumerate (size_signals):
        dwt_levels.append(dwt[i][:size])
    return dwt_levels

def get_size_signals(size_chunck, number_levels):
    size_signals = list()
    for i in range(1, NUMBER_LEVELS + 1):
        size = int(size_chunck / (2 ** (i)))
        size_signals.append(size)
    return size_signals

def get_axis(size_signals):
    i = 0
    axis = list()
    for i, size in enumerate(size_signals):
        x = np.array(range(1, size +1))
        x = np.multiply(x, (2**(i+1)))
        axis.append(x)
    return axis

def get_variance_signals(signals):
    signals_var = list()

    for data in signals:
        n = 0
        sum = 0
        sum_sqr = 0
        data_var = list()
        for x in data:
            n = n + 1
            sum = sum + x
            sum_sqr = sum_sqr + x * x
            if ( n - 1 != 0):
                variance = (sum_sqr - (sum * sum) / n) / (n - 1)
            else: 
                variance = 0 
            data_var.append(variance)
        signals_var.append(data_var)
        print (data)
        print (data_var)
        print (list(map(int,data_var)))
        print ()
    
    return signals_var

def energy_function (signals):
    energy_f = list()

    for signal in signals:
        e = (np.sum(np.array(signal)**2)) / len(signal)
        if (e > 0.):
            e = log2(e)
        else:
            e = 0.
        energy_f.append(e)
    return energy_f

def plot_signal_pcap_switch(switch_signal,test_filename):
    plotter.plot_signal(PCAP_SIGNAL, switch_signal, REPORT_DIR_PATH, test_filename)


def plot_dwt_switch(signal, type_signal,  type_coeff = "lp"):
    type_values     = "coeffs"
    type_signal_bg  = type_signal + "_library"

    size_signals    = get_size_signals(SIZE_CHUNCK, NUMBER_LEVELS)
    x_axis          = get_axis(size_signals)
    background_dwt  = get_py_dwt(signal, size_signals, NUMBER_LEVELS, type_coeff)
    switch_dwt      = loader.get_switch_levels_values(TEST_PREFIX, TEST_DIR_PATH, size_signals, type_values, type_coeff)

    report_filename = TEST_PREFIX + type_signal_bg + "_switch_" + type_coeff +"_" + type_values

    plotter.plot_signal_subplot(background_dwt, switch_dwt, x_axis, type_signal_bg, type_values, REPORT_DIR_PATH, report_filename)
    

def plot_variance_switch(signal, type_signal, type_coeff = "lp"):
    type_values_bg  = "coeffs"
    type_values     = "variance"
    type_signal_bg  = type_signal + "_library"

    size_signals    = get_size_signals(SIZE_CHUNCK, NUMBER_LEVELS)
    x_axis          = get_axis(size_signals)

    switch_dwt      = loader.get_switch_levels_values(TEST_PREFIX, TEST_DIR_PATH, size_signals, type_values_bg, type_coeff)

    background_var  = get_variance_signals(switch_dwt)
    switch_var      = loader.get_switch_levels_values(TEST_PREFIX, TEST_DIR_PATH, size_signals, type_values, type_coeff)

    report_filename = TEST_PREFIX + type_signal_bg + "_switch_" + type_coeff +"_" + type_values
    plotter.plot_signal_subplot(background_var, switch_var, x_axis, type_signal_bg, type_values, REPORT_DIR_PATH, report_filename)

    report_filename = report_filename +  "_last"
    plotter.plot_last_value(background_var, switch_var, type_values, REPORT_DIR_PATH, report_filename)

    report_filename = report_filename +  "_log2"
    plotter.plot_last_value_log(background_var, switch_var, type_values, REPORT_DIR_PATH, report_filename)

    if (type_coeff == "hp"):
        energy_switch = energy_function(switch_var)
        report_filename = TEST_PREFIX + type_signal_bg + "_switch_Energy"
        plotter.plot_energy(energy_switch, REPORT_DIR_PATH, report_filename)

def plot_snr_test_complete(signal, type_signal, type_coeff = "lp"):
    #plot complete test

    # plotter.plot_snr_test()


    print('***PLOT_SNR_TEST_COMPLETE')

def plot_snr_test_simple(signal, type_signal, type_plot = "simple"):

    #plot simple test
    type_signal_bg  = type_signal + "_library"
    
    signals_bg, signals_switch = loader.get_signal_snr_test(SNR_DATA, PCAP_DIR, TEST_DIR, SIZE_COUNT, SIZE_CHUNCK)

    signals_bg.append(PCAP_SIGNAL)
    signals_switch.append(signal)
    
    x = np.array(range(1, SIZE_CHUNCK +1))

    report_filename = TEST_PREFIX + type_signal_bg + "_switch_SNR_TEST_" + type_plot
    report_dirpath  = REPORT_DIR_PATH + "snr/"
    loader.directory_exist_checker(report_dirpath)

    plotter.plot_snr_test_signal(signals_bg, signals_switch, x, report_dirpath, report_filename)

    print("***PLOT_SNR_TEST_SIMPLE")    

def main():
    set_var_global()
    loader.directory_exist_checker(REPORT_DIR_PATH)

    test_filename = TEST_PREFIX + 'signal'    
    switch_signal = loader.extract_values_csv(TEST_DIR_PATH, test_filename)[:SIZE_CHUNCK]

    plot_signal_pcap_switch(switch_signal, test_filename)

    plot_dwt_switch(PCAP_SIGNAL,"PCAP", "lp")
    plot_dwt_switch(PCAP_SIGNAL,"PCAP", "hp")

    plot_dwt_switch(switch_signal,"SWITCH", "lp")
    plot_dwt_switch(switch_signal,"SWITCH", "hp")

    plot_variance_switch(switch_signal,"SWITCH", "lp")
    plot_variance_switch(switch_signal,"SWITCH", "hp")
    if (len(sys.argv) > 1):
        # flag = execute_current_option()
        type_test = sys.argv[1]
        if (type_test == '-t'):
            plot_snr_test_complete(switch_signal,"SWITCH", "lp")
        elif (type_test == "-s"):
            plot_snr_test_simple(switch_signal,"SWITCH", "lp")


if __name__ == '__main__':
    main()