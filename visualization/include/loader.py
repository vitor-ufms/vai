""" Loader from files utils """
import os
import numpy as np
from pandas.plotting import table 
from sklearn.metrics import r2_score

from scapy.all import rdpcap

LEVEL_NAME = ['signal', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']

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

def variance_by_item(samples):
    samples_var = list()

    for sample in samples:
        n = 0
        sum = 0
        sum_sqr = 0
        sample_var = list()
        for x in sample:
            n = n + 1
            sum = sum + x
            sum_sqr = sum_sqr + x * x
            if ( n - 1 != 0):
                variance = (sum_sqr - (sum * sum) / n) / (n - 1)
            else: 
                variance = 0 
            sample_var.append(variance)
        samples_var.append(sample_var)
    
    return samples_var

def energy_function(signals):
    energy_f = list()
    for signal in signals:
        e = (np.sum(np.array(signal)**2)) / len(signal)
        energy_f.append(e)
    return energy_f

def generate_signal_periodic(pps, slot_duration, size, size_count):
    pattern_array = np.append([pps * size_count], ([0] * (slot_duration - 1)))
    times = int(size / slot_duration) + 1
    signal = list(np.tile(pattern_array, times)[:size])
    return signal

def generate_dwt_axis(signal_duration, levels):
    i = 0
    axis = list()

    for i in range (1, levels + 1):
        size = int(signal_duration / (2 ** i))
        x = np.array(range(1, size + 1))
        x = np.multiply(x, (2 ** (i)))
        axis.append(x)
    return axis

def filenames_factory(filename_prefix, levels):
    filename_list = list()

    filename_list.append(filename_prefix + LEVEL_NAME[0])

    fn_base_level = filename_prefix + "level_"

    fn_dwt_list = list()
    for type in ("lp", "hp"):
        fn_list = list ()
        for i in range(1, levels + 1):
            fn_list.append(fn_base_level + LEVEL_NAME[i] + "_" + type + "_coeffs" )
        fn_dwt_list.append(fn_list)
    filename_list.append(fn_dwt_list)

    fn_var_list = list()
    for type in ("lp", "hp"):
        fn_list = list ()
        for i in range(1, levels + 1):
            fn_list.append(fn_base_level + LEVEL_NAME[i] + "_" + type + "_variance" )
        fn_var_list.append(fn_list)
    filename_list.append(fn_var_list)

    return filename_list

def extract_values_csv(dirpath, filename, size_number = 32):
    values = list()
    filepath = dirpath + filename + '.csv'
    with open(filepath, newline = '') as f:
        values = [ get_signed_number(int(item), size_number) for item in f.read().split(',')]
    return values

def packets_per_second(pkts):
    cntPktsPerSecond = {}

    for pkt in pkts:
        key = int(pkt.time)
        if key not in cntPktsPerSecond:
            cntPktsPerSecond[key] = 0
        cntPktsPerSecond[key] += 1
    
    return cntPktsPerSecond

def extract_values_pcap(file_dirpath, filename, size_count):

    pcap_filepath = file_dirpath + filename 
    packets  = rdpcap (pcap_filepath)

    count_pkts = packets_per_second(packets)
    
    list_pkt_per_second = list()
    for key in range(int(packets[0].time), int(packets[-1].time) + 1):
        if key not in count_pkts:
            list_pkt_per_second.append(0)
        else:
            list_pkt_per_second.append(count_pkts[key])
    
    signal = np.array(list_pkt_per_second) * size_count

    return signal