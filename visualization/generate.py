
from include import Signal, loader, plotter, table_image

DATA_DIR = "../reports/data/"
REPORT_DIR = "../reports/report/"
PCAP_DIR = "../utils/pcap/"
TEST_FILENAME_PREFIX = "fakebot_100pp4s_26_"
TEST_DIR = DATA_DIR + TEST_FILENAME_PREFIX + "/"
PCAP_FILENAME = "fakebot_100pp4s_26_out.pcap"
LEVEL = 7
DURATION = 2100
SIZE_COUNT = 10
PPS = 100
SLOT = 5

def generate_single_graphics(signal, data_origin, axis):
    report_dirpath = REPORT_DIR + TEST_FILENAME_PREFIX + '/' + data_origin + "/"
    loader.directory_exist_checker(report_dirpath)
    if (isinstance(signal, Signal.Signal)):
        plotter.signal_single_plot(signal.signal, SIZE_COUNT, data_origin, report_dirpath, TEST_FILENAME_PREFIX)
        plotter.dwt_single_plot(signal.a_coefficient, axis, "lp_" + data_origin + "_py", report_dirpath, TEST_FILENAME_PREFIX)
        plotter.dwt_single_plot(signal.d_coefficient, axis, "hp_" + data_origin + "_py", report_dirpath, TEST_FILENAME_PREFIX)
        plotter.variance_single_plot(signal.a_variance, axis, "lp_" + data_origin + "_py", report_dirpath, TEST_FILENAME_PREFIX)
        plotter.variance_single_plot(signal.d_variance, axis, "hp_" + data_origin + "_py", report_dirpath, TEST_FILENAME_PREFIX)
        plotter.variance_single_plot_last_value(signal.a_variance_last_value, "lp_" + data_origin + "_py", report_dirpath, TEST_FILENAME_PREFIX)
        plotter.variance_single_plot_last_value(signal.d_variance_last_value, "hp_" + data_origin + "_py", report_dirpath, TEST_FILENAME_PREFIX)
        plotter.variance_single_plot_last_value_log2(signal.a_variance_last_value_log2, "lp_" + data_origin + "_py", report_dirpath, TEST_FILENAME_PREFIX)
        plotter.variance_single_plot_last_value_log2(signal.d_variance_last_value_log2, "hp_" + data_origin + "_py", report_dirpath, TEST_FILENAME_PREFIX)
        plotter.energy_single_plot(signal.energy, data_origin + "_py", report_dirpath, TEST_FILENAME_PREFIX)
        # plotter.energy_single_plot_log2(signal.energy, data_origin + "_py", report_dirpath, TEST_FILENAME_PREFIX)
        
        if (isinstance(signal, Signal.Signal_csv)):
            plotter.dwt_single_plot(signal.a_coefficient_csv, axis, "lp_" + data_origin + "_csv", report_dirpath, TEST_FILENAME_PREFIX)
            plotter.dwt_single_plot(signal.d_coefficient_csv, axis, "hp_" + data_origin + "_csv", report_dirpath, TEST_FILENAME_PREFIX)
            plotter.variance_single_plot(signal.a_variance_csv, axis, "lp_" + data_origin + "_csv", report_dirpath, TEST_FILENAME_PREFIX)
            plotter.variance_single_plot(signal.d_variance_csv, axis, "hp_" + data_origin + "_csv", report_dirpath, TEST_FILENAME_PREFIX)
            plotter.variance_single_plot_last_value(signal.a_variance_last_value_csv, "lp_" + data_origin + "_csv", report_dirpath, TEST_FILENAME_PREFIX)
            plotter.variance_single_plot_last_value(signal.d_variance_last_value_csv, "hp_" + data_origin + "_csv", report_dirpath, TEST_FILENAME_PREFIX)
            plotter.variance_single_plot_last_value_log2(signal.a_variance_last_value_log2_csv, "lp_" + data_origin + "_csv", report_dirpath, TEST_FILENAME_PREFIX)
            plotter.variance_single_plot_last_value_log2(signal.d_variance_last_value_log2_csv, "hp_" + data_origin + "_csv", report_dirpath, TEST_FILENAME_PREFIX)
            plotter.energy_single_plot(signal.energy_csv, data_origin + "_csv", report_dirpath, TEST_FILENAME_PREFIX)
            # plotter.energy_single_plot_log2(signal.energy_csv, data_origin + "_csv", report_dirpath, TEST_FILENAME_PREFIX)

def generate_compare_tables(signals):
    report_dirpath = REPORT_DIR + TEST_FILENAME_PREFIX + '/' 
    loader.directory_exist_checker(report_dirpath)
    table_image.signals_compare_table(signals, report_dirpath, TEST_FILENAME_PREFIX)
    table_image.dwt_compare_table(signals, "lp", LEVEL, report_dirpath, TEST_FILENAME_PREFIX)
    table_image.dwt_compare_table(signals, "hp", LEVEL, report_dirpath, TEST_FILENAME_PREFIX)
    table_image.var_compare_table(signals, "lp", LEVEL, report_dirpath, TEST_FILENAME_PREFIX)
    table_image.var_compare_table(signals, "hp", LEVEL, report_dirpath, TEST_FILENAME_PREFIX)
    table_image.var_last_value_compare_table(signals, "lp", LEVEL, report_dirpath, TEST_FILENAME_PREFIX)
    table_image.var_last_value_compare_table(signals, "hp", LEVEL, report_dirpath, TEST_FILENAME_PREFIX)
    table_image.var_last_value_log_compare_table(signals, "lp", LEVEL, report_dirpath, TEST_FILENAME_PREFIX)
    table_image.var_last_value_log_compare_table(signals, "hp", LEVEL, report_dirpath, TEST_FILENAME_PREFIX)
    table_image.energy_compare_table(signals, LEVEL, report_dirpath, TEST_FILENAME_PREFIX)

def main ():
    filenames = loader.filenames_factory(TEST_FILENAME_PREFIX, LEVEL)
    axis = loader.generate_dwt_axis(DURATION, LEVEL)
    signals = list ()

    signal_switch  = Signal.Signal_csv(TEST_DIR, filenames[0] , LEVEL, DURATION)
    signal_switch.signal_dwt_lib()
    signal_switch.dwt_variance()
    signal_switch.energy_f()
    signal_switch.signal_dwt_csv(filenames[1])
    signal_switch.dwt_variance_csv(filenames[2])
    signal_switch.energy_f_csv()
    generate_single_graphics(signal_switch, "switch", axis)
    signals.append(signal_switch)

    signal_pcap    = Signal.Signal_pcap(PCAP_DIR, PCAP_FILENAME, SIZE_COUNT, LEVEL, DURATION)
    signal_pcap.signal_dwt_lib()
    signal_pcap.dwt_variance()
    signal_pcap.energy_f()
    generate_single_graphics(signal_pcap, "pcap", axis)
    signals.append(signal_pcap)

    signal_artificial = Signal.Signal(loader.generate_signal_periodic(PPS, SLOT, DURATION, SIZE_COUNT), LEVEL, DURATION)
    signal_artificial.signal_dwt_lib()
    signal_artificial.dwt_variance()
    signal_artificial.energy_f()
    generate_single_graphics(signal_artificial, "array", axis)
    signals.append(signal_artificial)

    generate_compare_tables(signals)


if __name__ == '__main__':
    main()