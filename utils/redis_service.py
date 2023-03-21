import redis
import sys
import os
import signal
import time

import argparse
import cmd
from collections import Counter
import os
import sys
import struct
import json
import csv
from functools import wraps
import bmpy_utils as utils

from bm_runtime.standard import Standard
from bm_runtime.standard.ttypes import *
try:
    from bm_runtime.simple_pre import SimplePre
except:
    pass
try:
    from bm_runtime.simple_pre_lag import SimplePreLAG
except:
    pass

#* ********************** CONSTANT VALUES ****************** *#
LEVEL_NAME = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
JSON_CONFIG_FILENAME = '../conf.json'
NUMBER_LEVELS = 7
FILEPATH = '../test/data/'
PREFIX_NAME = 'slingbot_port1_'

r = redis.Redis(host = '192.168.0.11', port = 6379, db = 0)

def signal_handler(sig, frame):
    print("Pressed Ctrl + C. Kill Redis stored service...")
    # size = len(r.lrange("signal", 0, -1))
    # print(size)
    register_names = load_register_names()
    for register_name in register_names:
        print(register_name)
        r.delete(register_name)
    sys.exit(0)

def get_signed_number(number, size_number = 32):
    signed = 0
    if  (number <= ((2 ** (size_number - 1)) - 1)):
        return number
    else:
        signed = number - (2 ** size_number)
        return signed

def set_var_global():
    with open(JSON_CONFIG_FILENAME) as json_file:
        data = json.load(json_file)

    global PCAP_FILENAME    
    global TEST_DIR    
    global TEST_PREFIX  
    global TEST_DIR_PATH  

    global NUMBER_LEVELS

    
    PCAP_FILENAME   = data["directories"]["PCAP_DIR"] + data["filenames"]["PCAP_FILENAME"]
    TEST_DIR        = data["directories"]["TEST_DIR"]
    TEST_PREFIX     = data["filenames"]["TEST_PREFIX"]

    NUMBER_LEVELS   = data["configuration"]["NUM_LEVELS"]


    TEST_DIR_PATH =  TEST_DIR + TEST_PREFIX + "/"

    print(TEST_DIR)
    print(TEST_PREFIX)
    print(NUMBER_LEVELS)
    print(TEST_DIR_PATH)

def directory_exist_checker(dir_path):
    exists = os.path.isdir(dir_path)
    if(exists):
        print("Exist directory for report: " + dir_path)
    else:
        os.makedirs(dir_path)
        print("Create directory for report: " + dir_path)

def enum(type_name, *sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())

    @staticmethod
    def to_str(x):
        return reverse[x]
    enums['to_str'] = to_str

    @staticmethod
    def from_str(x):
        return enums[x]

    enums['from_str'] = from_str
    return type(type_name, (), enums)

PreType = enum('PreType', 'None', 'SimplePre', 'SimplePreLAG')
ResType = enum('ResType', 'table', 'action_prof', 'action', 'meter_array',
               'counter_array', 'register_array')

def get_parser():

    class ActionToPreType(argparse.Action):
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            if nargs is not None:
                raise ValueError("nargs not allowed")
            super(ActionToPreType, self).__init__(option_strings, dest, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            assert(type(values) is str)
            setattr(namespace, self.dest, PreType.from_str(values))

    parser = argparse.ArgumentParser(description='BM runtime CLI')
    # One port == one device !!!! This is not a multidevice CLI
    parser.add_argument('--thrift-port', help='Thrift server port for table updates',
                        type=int, action="store", default=9090)

    parser.add_argument('--thrift-ip', help='Thrift IP address for table updates',
                        type=str, action="store", default='localhost')

    parser.add_argument('--json', help='JSON description of P4 program',
                        type=str, action="store", required=False)

    parser.add_argument('--pre', help='Packet Replication Engine used by target',
                        type=str, choices=['None', 'SimplePre', 'SimplePreLAG'],
                        default=PreType.SimplePre, action=ActionToPreType)

    parser.add_argument('--signal-size', help='Signal size',
                        type=int, action="store", default=6144)

    parser.add_argument('--sample-size', help='Sample size in data update',
                        type=int, action="store", default=16)

    return parser

REGISTER_ARRAYS = {}


# maps (object type, unique suffix) to object
SUFFIX_LOOKUP_MAP = {}


# services is [(service_name, client_class), ...]
def thrift_connect(thrift_ip, thrift_port, services):
    return utils.thrift_connect(thrift_ip, thrift_port, services)

class RegisterArray:
    def __init__(self, name, id_):
        self.name = name
        self.id_ = id_
        self.width = None
        self.size = None

        REGISTER_ARRAYS[name] = self

    def register_str(self):
        return "{0:30} [{1}]".format(self.name, self.size)

def reset_config():

    REGISTER_ARRAYS.clear()
    SUFFIX_LOOKUP_MAP.clear()

def load_json_str(json_str):
    def get_header_type(header_name, j_headers):
        for h in j_headers:
            if h["name"] == header_name:
                return h["header_type"]
        assert(0)

    def get_field_bitwidth(header_type, field_name, j_header_types):
        for h in j_header_types:
            if h["name"] != header_type: continue
            for t in h["fields"]:
                # t can have a third element (field signedness)
                f, bw = t[0], t[1]
                if f == field_name:
                    return bw
        assert(0)

    reset_config()
    json_ = json.loads(json_str)

    def get_json_key(key):
        return json_.get(key, [])

# Extract values from the registers
    for j_register in get_json_key("register_arrays"):
        register_array = RegisterArray(j_register["name"], j_register["id"])
        register_array.size = j_register["size"]
        register_array.width = j_register["bitwidth"]

    suffix_count = Counter()
    for res_type, res_dict in [
            (ResType.register_array, REGISTER_ARRAYS)]:
        for name, res in res_dict.items():
            suffix = None
            for s in reversed(name.split('.')):
                suffix = s if suffix is None else s + '.' + suffix
                key = (res_type, suffix)
                SUFFIX_LOOKUP_MAP[key] = res
                suffix_count[key] += 1
    for key, c in suffix_count.items():
        if c > 1:
            del SUFFIX_LOOKUP_MAP[key]

class RuntimeAPI(cmd.Cmd):
    prompt = 'RuntimeCmd: '
    intro = "Control utility for runtime P4 table manipulation"

    @staticmethod
    def get_thrift_services(pre_type):
        services = [("standard", Standard.Client)]

        if pre_type == PreType.SimplePre:
            services += [("simple_pre", SimplePre.Client)]
        elif pre_type == PreType.SimplePreLAG:
            services += [("simple_pre_lag", SimplePreLAG.Client)]
        else:
            services += [(None, None)]

        return services

    def get_res(self, type_name, name, res_type):
        key = res_type, name
        if key not in SUFFIX_LOOKUP_MAP:
            raise UIn_ResourceError(type_name, name)
        return SUFFIX_LOOKUP_MAP[key]

    def __init__(self, pre_type, standard_client, mc_client=None):
        cmd.Cmd.__init__(self)
        self.client = standard_client
        self.mc_client = mc_client
        self.pre_type = pre_type

def load_json_config(standard_client=None, json_path=None):
    load_json_str(utils.get_json_config(standard_client, json_path))

def load_register_names():
    register_names = [
        'signal'
        ]
    
    if (NUMBER_LEVELS > 0):
        for i in range(NUMBER_LEVELS):
            reg_name_prefix = "level_" + LEVEL_NAME[i]
            reg_name_suffix = ["_lp_coeffs", "_lp_variance", "_hp_coeffs", "_hp_variance"]
            for suffix in reg_name_suffix:
                reg_name = reg_name_prefix + suffix
                register_names.append(reg_name)

    return register_names



def extract_values_from_registers_to_redis(runtimeAPI, standard_client, sample_size, signal_size):

    reg_name_suffix = ["_lp_coeffs", "_lp_variance", "_hp_coeffs", "_hp_variance"]

    
    start = 0
    start_lvl = [0] * NUMBER_LEVELS
    end = 0
    end_lvl = [0] * NUMBER_LEVELS

    while True:
        time.sleep(sample_size)
        register_name = "signal"
        # save signal values in Redis list
        register = runtimeAPI.get_res("register", register_name, ResType.register_array)
        entries = standard_client.bm_register_read_all(0, register.name)
        end = start + sample_size
        print(end)
        for idx in range(start, end):
            if (idx >= signal_size):
                r.rpush(register_name, int(get_signed_number(entries[idx % signal_size])))
            else:
                r.rpush(register_name, int(get_signed_number(entries[idx])))
        print(r.lrange(register_name, 0, -1)) 
        print("Signal: Start: " + str(start) + ", End: " + str(end))
        start = end % signal_size

        for i in range (NUMBER_LEVELS):
            register_name_prefix = "level_" + LEVEL_NAME[i]

            if (i == 0):
                end_lvl[i] = int(end / 2)
            else:
                end_lvl[i] = int(end_lvl[i - 1] / 2)

            for sfx in reg_name_suffix:
                register_name = register_name_prefix + sfx
                register = runtimeAPI.get_res("register", register_name, ResType.register_array)
                entries = standard_client.bm_register_read_all(0, register.name)
                lvl_size = signal_size / (2 ** (i + 1))
                for idx in range(start_lvl[i],  end_lvl[i]):
                    if (idx >= lvl_size):
                        r.rpush(register_name, int(get_signed_number(entries[idx % lvl_size])))
                    else:
                        r.rpush(register_name, int(get_signed_number(entries[idx])))
                print(r.lrange(register_name, 0, -1)) 
            print( register_name + ": Start: " + str(start_lvl[i]) + ", End: " + str(end_lvl[i]))

            start_lvl[i] = end_lvl[i] % lvl_size


def main():

    args = get_parser().parse_args()
    print(args)

    standard_client, mc_client = thrift_connect(
        args.thrift_ip, args.thrift_port,
        RuntimeAPI.get_thrift_services(args.pre)
    )

    load_json_config(standard_client, args.json)
    runtimeAPI = RuntimeAPI(args.pre, standard_client, mc_client)
    # register_names = load_register_names()

    extract_values_from_registers_to_redis(runtimeAPI, standard_client, args.sample_size, args.signal_size)
    # while(True):
        
    #     extract_values_from_registers_to_redis(runtimeAPI, standard_client, register_names, idx, args.signal_size)
    #     # print(type(r.lrange("signal", 0, -1)))
    #     idx = idx + 2
    #     time.sleep(2)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    main()



