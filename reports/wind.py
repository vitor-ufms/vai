#!/usr/bin/env python3

"""     Main app for graphics reports   """

from hashlib import new
import math
from typing import List
import matplotlib.pyplot as plt
import numpy as np
from numpy.core.defchararray import add
from numpy.random import exponential, pareto
import pywt
from itertools import accumulate
from collections import Counter
import random


from includes import plotter, wavelet, loader


plt.style.use('seaborn')
palette = plt.get_cmap('Set1')
linewidth = 0.5
linewidthSingle = 1.0

DIRECTORY = "./wind/"
SIZE_CHUNCK = 1024
LEVELS = 10

def save_figure(fig, filename):
    if filename:
        fig.savefig(DIRECTORY + filename, dpi = 400, bbox_inches = 'tight')
    else:
        fig.show()

def finish_plot(filename):
    print("FINISHED: " + filename)

def get_size_signals(size_chunck):
    size_signals = list()
    for i in range(1, LEVELS + 1):
        size = int(size_chunck / (2 ** (i)))
        size_signals.append(size)
    
    # print (size_signals)
    return size_signals

def get_axis(size_signals):
    i = 0
    axis = list()
    for i, size in enumerate(size_signals):
        x = np.array(range(1, size +1))
        x = np.multiply(x, (2**(i+1)))
        axis.append(x)
    # print (axis)
    return axis

def get_log2(value):
    if (value == 0):
        return 0.
    else:
        return math.log2(value)

def exponential_signal(mean, flag):
    signal = list()
    arrive = list()
    prox = 0
    while (prox < float(SIZE_CHUNCK)):
        inter = exponential(mean,1)
        prox = prox + inter
        arrive.append(float(prox))

    if (flag == True):
        arrive.extend(pick_random(arrive, 8.))
        arrive.extend(pick_random(arrive, 18.))

    ceil_arrive = np.ceil(arrive).astype(int)
    cnt_arrive  = dict(Counter(ceil_arrive))

    for key in range (1, SIZE_CHUNCK + 1):
        if key not in cnt_arrive:
            signal.append(0)
        else:
            signal.append(cnt_arrive[key])
    return signal

def pick_random(array, value_add):

    size = int(len(array)/4)
    quarter = random.sample(array, size)
    quarter = np.array(quarter) + value_add
    return list(quarter)

    

    
def generate_signal_pattern():
    signal = list()
    pattern = [0, 0, 1, 1, 1, 1, 0, 0]
    signal.append(pattern * 128)

    print("Signal pattern generated...")
    return signal

def generate_signals_y():
    signals = list()
    
    y1 = exponential_signal(10, False) 
    signals.append(y1)
    y2 = exponential_signal(15, True)
    signals.append(y2) 

    print("Signal exponentially distributed generated...")
    return signals

def generate_signals_z():
    signals = list()
    signal_z1 = pareto(1.2,SIZE_CHUNCK)
    signals.append(signal_z1)
    signal_z2 = pareto(10,SIZE_CHUNCK)
    signals.append(signal_z2)

    print("Signal exponentially distributed generated...")
    return signals

def dwt_coeffs(signal, name_mother_wavelet = 'db1', level = 4):

    mother_wavelet = pywt.Wavelet(name_mother_wavelet)

    coeffs_A = list()
    coeffs_D = list()
    for i in range(1, level + 1):
        
        coeffs = pywt.downcoef('a', signal, mother_wavelet, mode = 'periodic', level = i)
        coeffs_A.append(coeffs)
        coeffs = pywt.downcoef('d', signal, mother_wavelet, mode = 'periodic', level = i)
        coeffs_D.append(coeffs)

    return coeffs_A, coeffs_D

# def dwt_coeffs(signal,name_mother_wavelet, level):
#     time_serie = signal
#     coeffs_A = list()
#     coeffs_D = list()

#     for i in range(1, level + 1):
#         cA = list()
#         cD = list()
#         for j in range(int(len(time_serie)/2)):
#             cA.append((1. / math.sqrt(2)) * (time_serie[2 * j] + time_serie[2 * j + 1]))
#             cD.append((1. / math.sqrt(2)) * (time_serie[2 * j] - time_serie[2 * j + 1]))
#         time_serie = cA
#         coeffs_A.append(cA)
#         coeffs_D.append(cD)
#     return coeffs_A, coeffs_D


def denormalization(signals, type = "a"):
    denorm_coeffs = list ()
    if (type == "a"):
        sign = 1
    elif (type == "d"):
        sign = -1
    else:
        print("Incorrect type!")
        return 0
    i = 1
    for signal in signals:
        denorm = np.array(signal) * (0.7071067812 ** i) * sign
        denorm_coeffs.append(denorm)

    return denorm_coeffs

def plot_signal(signals, filename):
    """
        Plots signal information, 
    """
    fig, ax = plt.subplots(figsize=(12, 4))

    title = filename
    i = 1
    for signal in signals:
        label  = 'signal_' + str(i)
        ax.plot(signal, marker = '', linewidth = 0.5, color = palette(i), label = label)
        i = i + 1 

    ax.set_title(title, loc = "center")
    ax.set(xlabel='Time', ylabel='Packets')

    ax.legend(bbox_to_anchor = (1.0, 1.0), fontsize = 'small')

    fig.tight_layout()

    save_figure(fig, filename)
    finish_plot(filename)

def plot_dwt_coeffs(signals, filename):
    number_plots = len(signals)
    fig, axs = plt.subplots(number_plots, figsize=(16,10))

    title = filename.lower()
    axs[0].set_title(title, loc = "center")
    
    size_signals    = get_size_signals(SIZE_CHUNCK)
    x_axis          = get_axis(size_signals)

    for i in range(number_plots):
        level = i + 1

        label  = " lvl" + str(level)

        x  = x_axis[i]
        y  = signals[i]

        axs[i].plot(x, y, marker = '', linewidth = 0.5, color = palette(level % 6), label = label)
        axs[i].legend(bbox_to_anchor = (1.0, 1.0), fontsize = 'small')

        axs[i].set_ylabel("coeffs")

    axs[-1].set_xlabel("Time", fontsize = 5)
    fig.tight_layout()

    save_figure(fig, filename)
    finish_plot(filename)

def plot_energy_function(signals, filename):
    """
        Plots signal information, 
    """
    fig, ax = plt.subplots(figsize=(12, 4))

    title = filename
    i = 1
    for signal in signals:
        signal_log2 = list(map(get_log2, signal))
        label  = 'signal_' + str(i)
        x = range(1,LEVELS + 1)
        ax.plot(x, signal_log2, marker = '*', linewidth = linewidthSingle, color = palette(i), label = label)
        i = i + 1 

    ax.set_title(title, loc = "center")
    ax.set(xlabel='Level', ylabel='Log2(Energy(d j))')


    ax.legend(bbox_to_anchor = (1.0, 1.0), fontsize = 'small')

    fig.tight_layout()

    save_figure(fig, filename)
    finish_plot(filename)

def energy_function(signals):
    energy_f = list()
    for signal in signals:
        e = (np.sum(np.array(signal)**2)) / len(signal)
        energy_f.append(e)
    # print(energy_f)
    return energy_f

def main():
    loader.directory_exist_checker(DIRECTORY)

    # energy = list()
    # signal = generate_signal_pattern()
    # coeffs_A, coeffs_D = dwt_coeffs(signal[0], "db1", LEVELS)
    # energy.append(energy_function(coeffs_D))

    # plot_signal(signal, "signal_pattern")
    # plot_dwt_coeffs(coeffs_A,"signal_pattern_coeffs_aprox")
    # plot_dwt_coeffs(coeffs_D,"signal_pattern_coeffs_detail")
    # plot_energy_function(energy,"signal_pattern_energy")

    
    energy = list()

    signals_Y = generate_signals_y()
    i = 1
    plot_signal(signals_Y, "signals_exponentially_distributed")
    for signal in signals_Y:
        coeffs_A, coeffs_D = dwt_coeffs(signal, "db1", LEVELS)
        energy.append(energy_function(coeffs_D))
        plot_dwt_coeffs(coeffs_A,"signal_Y" + str(i)+ "_coeffs_aprox")
        plot_dwt_coeffs(coeffs_D,"signal_Y" + str(i)+ "_coeffs_detail")
        i = i + 1
    plot_energy_function(energy, "signals_Y_energy")


    # energy = list()

    # signals_Z = generate_signals_z()
    # i = 1
    # plot_signal(signals_Z, "signals_pareto_distributed")
    # for signal in signals_Y:
    #     coeffs_A, coeffs_D = dwt_coeffs(signal, "db1", LEVELS)
    #     energy.append(energy_function(coeffs_D))
    #     plot_dwt_coeffs(coeffs_A,"signal_Z" + str(i)+ "_coeffs_aprox")
    #     plot_dwt_coeffs(coeffs_D,"signal_Z" + str(i)+ "_coeffs_detail")
    #     i = i + 1
    # plot_energy_function(energy, "signals_Z_energy")


if __name__ == '__main__':
    main()