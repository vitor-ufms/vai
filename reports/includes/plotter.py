""" Plotter utils """

import math
import matplotlib.pyplot as plt
import numpy as np
import itertools

from sklearn.metrics import r2_score


#* ********************** Settings for plot ****************** *#
plt.style.use('seaborn')
palette = plt.get_cmap('Set1')
linewidth = 0.5
linewidthSingle = 1.0
# font = {'family' : 'monospace',
#         'weight' : 'normal',
#         'size'   : 6}

# plt.rc('font', **font)

def snr_db(signal, noise):
    p_signal = np.var(signal)
    p_noise = np.var(noise)

    ratio     = float(p_signal) / float(p_noise)
    ratio_db  = 10.0 * math.log10(ratio)

    return ratio_db

def save_figure(fig, filename, directory):
    if filename:
        fig.savefig(directory + filename, dpi = 600, bbox_inches = 'tight')
    else:
        fig.show()

def get_last_value(array):
        return array[-1]

def get_last_value_log(array):
    if (array[-1] == 0):
        return 0.
    else:
        return math.log2(array[-1])

def finish_plot(filename):
    print("FINISHED: " + filename)

def annotation_operator(x_list, y_list, type_operator):
    x_list = np.array(x_list)
    y_list = np.array(y_list)
    x, y = 0., 0. 

    if  (type_operator == 'max'):
        x = x_list[np.argmax(y_list)]
        y = y_list.max()
    elif (type_operator == 'min'):
        x = x_list[np.argmin(y_list)]
        y = y_list.min()

    text_format = "y={:.3f}".format(y)

    plt.annotate(text_format, xy=(x, y))

def annotation_values(ax, x, y):
    style = dict(size = 7, color = 'purple')
    for i in range(len(x)):
        y_str = "{:.3f}".format(y[i])
        ax.text(x[i], y[i], y_str, ha='right', **style)

def plot_signal(signal_bg, switch, directory, filename = None):
    """
        Plots signal information, 
    """
    fig, ax = plt.subplots(figsize=(36, 6))

    title = "PCAP library and SWITCH values" 
    label1  = 'PCAP library'
    label2  = 'SWITCH'

 
    ax.plot(signal_bg, marker = '', linewidth = linewidthSingle, color = palette(8), label = label1)
    ax.plot(switch, marker = '', linewidth = linewidthSingle, color = palette(1), label = label2)
    

    ax.set_title(title, loc = "center")
    ax.set(xlabel='Time', ylabel='Packets')

    R2 = r2_score(signal_bg, switch)
    r2_format = "{:.5e}".format(R2)

    var = np.var(switch)
    var_format = "{:.5e}".format(var)

    title_legend   = "R2: " + r2_format + "\n Var: " + var_format
    ax.legend(bbox_to_anchor = (1.0, 1.0), fontsize = 'small', title = title_legend)

    fig.tight_layout()

    save_figure(fig, filename, directory)
    finish_plot(filename)

def plot_signal_subplot(signal_bg, switch, x_axis, type_signal_bg, type_values, directory, filename = None):

    """Plot values from signal background library and switch values from CSV files

    Args:
        signal_bg(list), 
        switch, 
        x_axis,
        type_signal_bg: ;values: "PCAP library", "SWITCH library" 
        directory, 
        filename

    """
    number_plots = len(signal_bg)
    fig, axs = plt.subplots(number_plots)

    title = filename.lower()
    axs[0].set_title(title, loc = "center")

    for i in range(number_plots):
        level = i + 1

        label1  = " lvl" + str(level)+ '-' + type_signal_bg
        label2  = " lvl" + str(level)+ '-' + 'SWITCH' 

        x   = x_axis[i]
        y1  = signal_bg[i]
        y2  = switch[i]

        axs[i].plot(x, y1, marker = '', linewidth = linewidth, color = palette(8), label = label1)
        axs[i].plot(x, y2, marker = '', linewidth = linewidth, color = palette(level % 6), label = label2)

        R2 = r2_score(signal_bg[i], switch[i])
        r2_format = "{:.5e}".format(R2)

        title_legend   = "R2: " + r2_format
        legend = axs[i].legend(bbox_to_anchor = (1.0, 1.0), fontsize = 'xx-small', title = title_legend)
        legend.get_title().set_fontsize('x-small')

        axs[i].set_ylabel(type_values, fontsize = 5)
        axs[i].tick_params(axis='both', which='major', labelsize=5)

    axs[-1].set_xlabel("Time", fontsize = 5)
    fig.tight_layout()
    save_figure(fig, filename, directory)
    finish_plot(filename)

def plot_last_value(values_bg, values, type_values, directory, filename = None):
        
    """
        Plots last values
    """
    fig, ax = plt.subplots(figsize=(12, 4))

    title = filename.lower()
    label1  = type_values.upper() + ' library'
    label2  = 'SWITCH'

    values_bg   = list(map(get_last_value, values_bg))
    values      = list(map(get_last_value, values))
 
    x = range(1, len(values) + 1)

    ax.plot(x, values_bg, marker = '', linewidth = linewidthSingle, color = palette(8), label = label1)
    ax.plot(x, values, marker = '', linewidth = linewidthSingle, color = palette(1), label = label2)
    

    ax.set_title(title, loc = "center")
    if (type_values == "variance"):
        ax.set(xlabel='Levels', ylabel="var")
    else:     
        ax.set(xlabel='Levels', ylabel=type_values)

    R2 = r2_score(values_bg, values)
    r2_format = "{:.5e}".format(R2)

    title_legend   = "R2: " + r2_format
    ax.legend(bbox_to_anchor = (1.0, 1.0), fontsize = 'small', title = title_legend)

    annotation_values(ax, x, values)

    fig.tight_layout()

    save_figure(fig, filename, directory)
    finish_plot(filename)

def plot_last_value_log(values_bg, values, type_values, directory, filename = None):
        
    """
        Plots last values
    """
    fig, ax = plt.subplots(figsize=(12, 4))

    title = filename.lower()
    label1  = type_values.upper() + ' library'
    label2  = 'SWITCH'

    values_bg   = list(map(get_last_value_log, values_bg))
    values      = list(map(get_last_value_log, values))
 
    x = range(1, len(values) + 1)

    ax.plot(x, values_bg, marker = '', linewidth = linewidthSingle, color = palette(8), label = label1)
    ax.plot(x, values, marker = '', linewidth = linewidthSingle, color = palette(1), label = label2)
    

    ax.set_title(title, loc = "center")
    if (type_values == "variance"):
        ax.set(xlabel='Levels', ylabel="log2(var)")
    else:     
        ax.set(xlabel='Levels', ylabel=type_values)

    R2 = r2_score(values_bg, values)
    r2_format = "{:.5e}".format(R2)

    title_legend   = "R2: " + r2_format
    ax.legend(bbox_to_anchor = (1.0, 1.0), fontsize = 'small', title = title_legend)

    annotation_values(ax, x, values)

    fig.tight_layout()

    save_figure(fig, filename, directory)
    finish_plot(filename)


def plot_snr_test_signal(signal_bg, switch, x_axis, directory, filename = None):

    """Plot values periodic signal, noise signal and Signal evaluated
    Args:
        signal_bg(list), 
        switch, 
        x_axis,
        type_signal_bg: ;values: "PCAP library", "SWITCH library" 
        directory, 
        filename

    """
    number_plots = len(signal_bg)
    fig, axs = plt.subplots(number_plots)
    labels = ["Periodic", "Noise", "Signal Final"]
    for i in range(number_plots):
        level = i + 1

        label1  = labels[i] + '-' + "PCAP"
        label2  = labels[i] + '-' + 'SWITCH' 

        x   = x_axis
        y1  = signal_bg[i]
        y2  = switch[i]

        axs[i].plot(x, y1, marker = '', linewidth = linewidth, color = palette(8), label = label1)
        axs[i].plot(x, y2, marker = '', linewidth = linewidth, color = palette(level % 6), label = label2)

        R2 = r2_score(signal_bg[i], switch[i])
        r2_format = "{:.5e}".format(R2)


        title_legend   = "R2: " + r2_format
        legend = axs[i].legend(bbox_to_anchor = (1.0, 1.0), fontsize = 'xx-small', title = title_legend)
        legend.get_title().set_fontsize('x-small')

        axs[i].set_ylabel("Packets", fontsize = 5)
        axs[i].tick_params(axis='both', which='major', labelsize=5)


    snr = snr_db(switch[0], switch[1])
    snr_format = "{:.1E}".format(snr)

    xlabel = "Time" + " - SNR: " + snr_format
    axs[-1].set_xlabel(xlabel, fontsize = 5)
    # fig.tight_layout()
    save_figure(fig, filename, directory)
    finish_plot(filename)

def plot_energy(values, directory, filename = None):
        
    """
        Plots last values
    """
    fig, ax = plt.subplots(figsize=(12, 4))

    title = filename.lower()
    label2  = 'SWITCH'
 
    x = range(1, len(values) + 1)

    
    ax.plot(x, values, marker = '', linewidth = linewidthSingle, color = palette(1), label = label2)
    
    ax.set_title(title, loc = "center")
    ax.set(xlabel='Levels', ylabel='Log2(Energy(Level))')


    ax.legend(bbox_to_anchor = (1.0, 1.0), fontsize = 'small')

    annotation_values(ax, x, values)

    fig.tight_layout()

    save_figure(fig, filename, directory)
    finish_plot(filename)