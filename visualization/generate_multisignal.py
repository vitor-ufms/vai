
from include import Signal, loader, plotter, table_image

DATA_DIR = "../reports/data/"
REPORT_DIR = "../reports/report/"
PCAP_DIR = "../utils/pcap/"
TEST_FILENAME_PREFIX = "multisignal-"
TEST_DIR = DATA_DIR + TEST_FILENAME_PREFIX + "/"
# PCAP_FILENAME = "fakebot_100pp5s_17_out.pcap"
LEVEL = 7
DURATION = 300
SIZE_COUNT = 10
PPS = 100
SLOT = 9


def generate_graphics(signals, data_origin):
    report_dirpath = REPORT_DIR + TEST_FILENAME_PREFIX + '/' + data_origin + "/"
    loader.directory_exist_checker(report_dirpath)

    plotter.multisignal_single_plot(signals[0], SIZE_COUNT, data_origin, report_dirpath, TEST_FILENAME_PREFIX)
    plotter.variance_multisignal_plot_last_value(signals[1], "lp-" + data_origin , report_dirpath, TEST_FILENAME_PREFIX)
    plotter.variance_multisignal_plot_last_value(signals[2], "hp-" + data_origin , report_dirpath, TEST_FILENAME_PREFIX)

def main ():
    filenames = loader.filenames_factory(TEST_FILENAME_PREFIX, LEVEL)
    axis = loader.generate_dwt_axis(DURATION, LEVEL)
    signals = list ()

    list_aS = list()
    list_aS_avar = list()
    list_aS_dvar = list()

    for i in [4,5,8]:
        slot = i
        print(slot)
        aS = Signal.Signal(loader.generate_signal_periodic(PPS, slot, DURATION, SIZE_COUNT), LEVEL, DURATION)
        aS.signal_dwt_lib()
        aS.dwt_variance()
        aS.energy_f()
        list_aS.append(aS.signal)
        list_aS_avar.append(aS.a_variance_last_value)
        list_aS_dvar.append(aS.d_variance_last_value)
    
    
    generate_graphics([list_aS, list_aS_avar, list_aS_dvar], "artificial")
 

if __name__ == '__main__':
    main()