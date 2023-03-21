
from math import log2
from numpy.lib.npyio import load
from include import loader, wavelet

padding = 0

class Signal :

    def __init__(self, signal, levels, size):
        self.signal  = signal[padding:size]
        self.levels  = levels
        self.size    = size
        self.a_coefficient = list()
        self.d_coefficient = list()
        self.a_variance = list()
        self.d_variance = list()
        self.a_variance_last_value = list()
        self.d_variance_last_value = list()
        self.a_variance_last_value_log2 = list()
        self.d_variance_last_value_log2= list()
        self.energy = list()
    
    def signal_dwt_lib(self):
        self.a_coefficient  = wavelet.dwt_coeffs(self.signal, "db1", self.levels, "lp")
        self.d_coefficient  = wavelet.dwt_coeffs(self.signal, "db1", self.levels, "hp")

    def dwt_variance(self):
        self.a_variance = loader.variance_by_item(self.a_coefficient)
        self.a_variance_last_value = [item[-1] for item in self.a_variance]
        self.a_variance_last_value_log2 = [log2(item) if item > 0. else 0. for item in self.a_variance_last_value]
        self.d_variance = loader.variance_by_item(self.d_coefficient)
        self.d_variance_last_value = [item[-1] for item in self.d_variance]
        self.d_variance_last_value_log2 = [log2(item) if item > 0. else 0. for item in self.d_variance_last_value]

    def energy_f(self):
        self.energy = loader.energy_function(self.d_coefficient)
        self.energy = [log2(item) if item > 0. else 0. for item in self.energy]



class Signal_csv (Signal):
    def __init__(self, csv_dp, csv_fn, levels, size):
        self.csv_dirpath  = csv_dp
        self.a_coefficient_csv = list()
        self.d_coefficient_csv = list()
        self.a_variance_csv = list()
        self.d_variance_csv = list()
        self.a_variance_last_value_csv = list()
        self.d_variance_last_value_csv = list()
        self.a_variance_last_value_log2_csv = list()
        self.d_variance_last_value_log2_csv = list()
        self.energy_csv = list()
        signal = loader.extract_values_csv(self.csv_dirpath, csv_fn)[:size]
        super().__init__(signal, levels, size)

    def signal_dwt_csv(self, csv_fn_list):

        for i, fn in enumerate(csv_fn_list[0]):
            dwt = loader.extract_values_csv(self.csv_dirpath, fn)
            self.a_coefficient_csv.append(dwt[int(padding/(2 ** (i + 1))):int(self.size/(2 ** (i + 1)))])

        for i, fn in enumerate(csv_fn_list[1]):
            dwt = loader.extract_values_csv(self.csv_dirpath, fn)
            self.d_coefficient_csv.append(dwt[int(padding/(2 ** (i + 1))):int(self.size/(2 ** (i + 1)))])

    def dwt_variance_csv(self, csv_fn_list):

        for i, fn in enumerate(csv_fn_list[0]):
            var = loader.extract_values_csv(self.csv_dirpath, fn)
            self.a_variance_csv.append(var[int(padding/(2 ** (i + 1))):int(self.size/(2 ** (i + 1)))])
            self.a_variance_last_value_csv = [item[-1] for item in self.a_variance_csv]
            self.a_variance_last_value_log2_csv = [log2(item) if item > 0. else 0. for item in self.a_variance_last_value_csv]

        for i, fn in enumerate(csv_fn_list[1]):
            var = loader.extract_values_csv(self.csv_dirpath, fn)
            self.d_variance_csv.append(var[int(padding/(2 ** (i + 1))):int(self.size/(2 ** (i + 1)))])
            self.d_variance_last_value_csv = [item[-1] for item in self.d_variance_csv]
            self.d_variance_last_value_log2_csv = [log2(item) if item > 0. else 0. for item in self.d_variance_last_value_csv]

    def energy_f_csv(self):
        self.energy_csv = loader.energy_function(self.d_coefficient_csv)
        self.energy_csv = [log2(item) if item > 0. else 0. for item in self.energy_csv]

class Signal_pcap (Signal):
    def __init__(self, pcap_dp, pcap_fn, size_count, levels, size):
        self.pcap_dirpath  = pcap_dp
        self.pcap_filename = pcap_fn
        self.size_count    = size_count
        signal = loader.extract_values_pcap(self.pcap_dirpath, self.pcap_filename, size_count)
        
        super().__init__(signal, levels, size)