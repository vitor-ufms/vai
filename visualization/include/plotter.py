""" Plotter utils """

from math import log2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import table 

from sklearn.metrics import r2_score

#* ********************** Settings for plot ****************** *#
plt.style.use('seaborn')
palette = plt.get_cmap('Set1')
linewidth = 1
linewidthSingle = 1
plt.rcParams['axes.facecolor'] = '#efefef'
plt.rc('xtick', labelsize=15)

def generate_message(filename):
    print("Generating  " + filename + " ...")

def finish_plot(filename):
    print("FINISHED: " + filename)

def save_figure(fig, directory, filename):
    if filename:
        fig.savefig(directory + filename, dpi = 600, bbox_inches = 'tight')
    else:
        fig.show()

def signal_single_plot(signal, size_count, type,  dirpath, filename_prefix):
    filename = filename_prefix + "signal_" + type
    generate_message(filename)
    labels = ["Time (s)", "Packets * " + str(size_count)]

    fig = single_plot(signal, filename, labels, 1)

    save_figure(fig, dirpath, filename)
    finish_plot(filename)

def multisignal_single_plot(signals, size_count, type,  dirpath, filename_prefix):
    filename = filename_prefix + "signal-" + type 
    generate_message(filename)
    labels = ["Time (s)", "Signal "]

    fig = multiple_plot2(signals, filename, labels)

    save_figure(fig, dirpath, filename)
    finish_plot(filename)

def dwt_single_plot(signals, axis, type,  dirpath, filename_prefix):
    filename = filename_prefix + "dwt_" + type
    generate_message(filename)
    labels = ["Time (s)", "Level "]

    fig = multiple_plot(signals, axis, filename, labels)

    save_figure(fig, dirpath, filename)
    finish_plot(filename)

def variance_single_plot(signals, axis, type,  dirpath, filename_prefix):
    filename = filename_prefix + "var_" + type
    generate_message(filename)
    labels = ["Time (s)", "Level"]

    fig = multiple_plot(signals, axis, filename, labels)

    save_figure(fig, dirpath, filename)
    finish_plot(filename)

def variance_single_plot_last_value(signal, type,  dirpath, filename_prefix):
    filename = filename_prefix + "var_last_value_" + type 
    generate_message(filename)
    labels = ["Level", "Var"]

    fig = single_plot(signal, filename, labels)

    save_figure(fig, dirpath, filename)
    finish_plot(filename)

def variance_multisignal_plot_last_value(signals, type,  dirpath, filename_prefix):
    filename = filename_prefix + "var-" + type 
    generate_message(filename)
    labels = ["Level", "Signal"]

    fig = multiple_plot2(signals, filename, labels)

    save_figure(fig, dirpath, filename)
    finish_plot(filename)

def variance_single_plot_last_value_log2(signal, type,  dirpath, filename_prefix):
    filename = filename_prefix + "log2(var)_last_value_" + type 
    generate_message(filename)
    labels = ["Level", "Log2(Var)"]

    fig = single_plot(signal, filename, labels)

    save_figure(fig, dirpath, filename)
    finish_plot(filename)

def energy_single_plot(signal, type,  dirpath, filename_prefix):
    filename = filename_prefix + "energy_" + type 
    generate_message(filename)
    labels = ["Level", "Log2(Energy)"]

    fig = single_plot(signal, filename, labels)

    save_figure(fig, dirpath, filename)
    finish_plot(filename)


def single_plot(signal, filename, labels, linewidth = 0.5):
    fig, ax = plt.subplots(figsize=(12, 4))

    title = filename
    x = range (1, len(signal) + 1)

    ax.plot(x, signal, marker = '', linewidth = linewidth, color = palette(1))

    # ax.set_title(title, loc = "center")
    ax.set(xlabel = labels[0], ylabel = labels[1])

    # ax.legend(fontsize = 'small')

    fig.tight_layout()
    return fig

def single_compare_plot(signals, filename):
    fig, ax = plt.subplots(figsize=(12, 4))

    title = filename
    i = 1
    for signal in signals:
        label  = 'signal_' + str(i)
        ax.plot(signal, marker = '', linewidth = linewidth, color = palette(i), label = label)
        i = i + 1 

    # ax.set_title(title, loc = "center")
    ax.set(xlabel='Time', ylabel='Packets')

    ax.legend(bbox_to_anchor = (1.0, 1.0), fontsize = 'small')

    fig.tight_layout()
    return fig

def multiple_plot2(signals, filename, labels, linewidth = 1.0):
    number_plots = len(signals)
    fig, axs = plt.subplots(number_plots, figsize=(16,10))

    for i, signal in enumerate(signals):
        x = range (len(signal) + 1)
        label  = " sgn" + str(i + 1)

        axs[i].plot(x[1:], signal, marker = '', linewidth = linewidth, color = palette(i % 5), label = label)
        print (x[1:])
        # axs[i].set_xticklabels(fontsize=15)
        print(x)
        axs[i].set_ylabel(labels[1] + str(i + 1), fontsize = 20)

    axs[-1].set_xlabel(labels[0], fontsize = 20)
    fig.tight_layout()

    return fig

def multiple_plot(signals, axis, filename, labels):

    number_plots = len(signals)
    fig, axs = plt.subplots(number_plots, figsize=(16,10))

    # title = filename.lower()
    # axs[0].set_title(title, loc = "center")
    
    x_axis = axis

    for i, signal in enumerate(signals):
        label  = " Lvl" + str(i + 1)

        x  = x_axis[i]
        y  = signal[:len(x)]

        axs[i].plot(x, y, marker = '', linewidth = linewidth, color = palette(i % 5), label = label)
        # axs[i].legend( fontsize = 'small')

        axs[i].set_ylabel(labels[1] + str(i + 1))

    axs[-1].set_xlabel(labels[0], fontsize = 12)
    fig.tight_layout()

    return fig