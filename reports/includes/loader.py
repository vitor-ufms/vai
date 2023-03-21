""" Loader from files utils """
import argparse
import sys
import socket
import random

import os

import time
import json


import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import numpy as np
import csv

from scapy.all import sniff, rdpcap
from scapy.all import sendp
from scapy.all import get_if_list, get_if_hwaddr


#* ********************** CONSTANT VALUES ****************** *#
LEVEL_NAME = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']


def directory_exist_checker(dir_path):
    exists = os.path.isdir(dir_path)
    if(exists):
        print("Exist directory for report: " + dir_path)
    else:
        os.makedirs(dir_path)
        print("Create directory for report: " + dir_path)

def get_signed_number(number, size_number = 32):
    signed = 0
    if  (number <= ((2 ** (size_number - 1) )- 1)):
        return number
    else:
        signed = number - (2** size_number)
        return signed

def packets_per_second(pkts):
    cntPktsPerSecond = {}

    cnt = 0
    for pkt in pkts:
        key = int(pkt.time)
        if key not in cntPktsPerSecond:
            cntPktsPerSecond[key] = 0
        cntPktsPerSecond[key] += 1
        cnt = cnt +1
    print(cnt)
    
    return cntPktsPerSecond

def extract_values_csv(dirpath, filename, size_number = 32):
    values = list()
    filepath = dirpath + filename + '.csv'
    with open(filepath, newline = '') as f:
        values = [ get_signed_number(int(item), size_number) for item in f.read().split(',')]
    return values


def get_signal_from_pcap(filepath, delay, padding, size_count):

    pcap_filepath = filepath 
    packets  = rdpcap (pcap_filepath)

    size_chunck = int(packets[-1].time)-int(packets[0].time) + 1 + delay

    count_pkts = packets_per_second(packets)
    
    list_pkt_per_second = list()
    for key in range(int(packets[0].time), int(packets[-1].time) + 1 + delay):
        if key not in count_pkts:
            list_pkt_per_second.append(0)
        else:
            list_pkt_per_second.append(count_pkts[key])
    
    signal = (np.array(list_pkt_per_second) + padding) * size_count

    return signal, size_chunck

def get_switch_levels_values(file_prefix, dir_path, size_signals, type_values = "coeffs", type_coeff = "lp"):
    """Get and extract values of the switch from CSV files

    Args:
        file_prefix (str): Prefix of filename for extract
        dir_path (str): directory path of filename for extract
        size_signals (list): 
        type_values (str): Type of values that will be extract; values:"coeffs"(Default), "variance"
        type_coeff (str): Type of coefficients values that will be extract; values:"lp"(Default), "hp"

    Returns:
        list: list of coefficients from levels decomposition
    """
    levels_value = list()
    number_levels = len(size_signals)
    for i in range (0, number_levels):
        size = size_signals[i]
        test_filename = file_prefix + 'level_' + LEVEL_NAME[i] + '_' + type_coeff + '_' + type_values
        level_value = extract_values_csv(dir_path, test_filename)[:size]
        levels_value.append(level_value)
    return levels_value

def get_signal_snr_test(SNR_DATA, PCAP_DIR, TEST_DIR, SIZE_COUNT, SIZE_CHUNCK):
    periodic_pcap_filepath = PCAP_DIR + SNR_DATA["PERIODIC_SIGNAL"]["PCAP_FILENAME"]
    periodic_pcap_signal, size = get_signal_from_pcap(periodic_pcap_filepath, 0, 0, SIZE_COUNT)
    periodic_pcap_signal = periodic_pcap_signal[:SIZE_CHUNCK]
    noise_pcap_filepath = PCAP_DIR + SNR_DATA["NOISE_SIGNAL"]["PCAP_FILENAME"]
    noise_pcap_signal, size = get_signal_from_pcap(noise_pcap_filepath, 0, 0, SIZE_COUNT)[:SIZE_CHUNCK]
    noise_pcap_signal = noise_pcap_signal[:SIZE_CHUNCK]

    signals_bg = [periodic_pcap_signal, noise_pcap_signal]

    periodic_switch_filepath = TEST_DIR + SNR_DATA["PERIODIC_SIGNAL"]["TEST_PREFIX"] + "/"
    periodic_switch_filename = SNR_DATA["PERIODIC_SIGNAL"]["TEST_PREFIX"] + "signal"
    periodic_switch_signal = extract_values_csv(periodic_switch_filepath, periodic_switch_filename)[:SIZE_CHUNCK]
    noise_switch_filepath = TEST_DIR + SNR_DATA["NOISE_SIGNAL"]["TEST_PREFIX"] + "/"
    noise_switch_filename = SNR_DATA["NOISE_SIGNAL"]["TEST_PREFIX"] + "signal"
    noise_switch_signal = extract_values_csv(noise_switch_filepath, noise_switch_filename)[:SIZE_CHUNCK]

    signals_switch = [periodic_switch_signal, noise_switch_signal]

    return signals_bg, signals_switch