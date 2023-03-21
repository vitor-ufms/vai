#!/usr/bin/env python


# python send_fakebot.py 10.0.2.2 -p 10 -s 14

import argparse
import sys, getopt
import socket
import random
import struct
import time
import os
import time

from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP

def get_options():
    short_options   = "p:m:d:s:t:i:"
    long_options    = ["packets", "message", "duration", "sleep", "time", "interval"]

    return short_options, long_options

def set_options(arguments_list):
    options = get_options()
    try:
        arguments, values = getopt.getopt(arguments_list, options[0], options[1])
    except getopt.error as err:
        print(str(err))
        sys.exit(2)
    
    return arguments    


def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

def finish_ring():
    # Ring when the process finish 
    duration = 2
    freq = 2500
    os.system('play -nq -t alsa synth {} sine {}'.format(duration,freq))
    os.system('spd-say "Your program has finished"') 

def main():
    num_seconds = 300
    message = 'Hi p4'
    num_packets = 100
    num_seconds_sleep = 0
    interval_length = 0.
    duration = 1.


    if len(sys.argv)<3:
        print 'pass 2 arguments: <destination> "<message>"'
        exit(1)

    args_list       = sys.argv
    args_list_opt   = args_list[2:]
    args            = set_options(args_list_opt)

    for current_argument, current_value in args:
        if  current_argument in ("-t", "--time"):
            num_seconds         = int(current_value)    
        elif current_argument in ("-m", "--message"):
            message             = current_value
        elif current_argument in ("-p", "--packets"):
            num_packets         = int(current_value)
        elif current_argument in ("-s", "--sleep"):
            num_seconds_sleep   = int(current_value)
        elif current_argument in ("-d", "--duration"):
            duration            = int(current_value)
        elif current_argument in ("-i", "--interval"):
            interval_length     = int(current_value)
            print(interval_length)
        else:
            print("-- Any args")

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()


    iter = int(num_seconds / (interval_length)) + 2

    print("#ITER: " + str(iter) )
    print("#packets: " + str(num_packets))
    print("#duration: " + str(duration))
    print("#time: " + str(num_seconds))
    print("#interval_length: " + str(interval_length))

    cli = "tcpreplay -i eth0 --maxsleep 5 " + " ../utils/pcap/" + str(num_packets) + ".pcap"
    print(cli)

    start_interval = time.time()
    print(start_interval)
    print(type(start_interval))
    for i in range(iter):
        print("#ITER: " + str(i) )
        # print "sending on interface %s to %s" % (iface, str(addr))
        # pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        # pkt = pkt /IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / message
        # # pkt.show2()
        # inter = float(duration)/float(num_packets)
        # print("#INTER:  " + str(inter))
        # sendp(pkt, iface=iface, verbose=False, count = num_packets, inter = inter )
        # # sendp(pkt, iface=iface, verbose=False)
        start_interval = start_interval + float(interval_length)
        os.system(cli)
        num_seconds_sleep = start_interval - time.time()
        time.sleep(num_seconds_sleep)

        # time.sleep(1)

    finish_ring()

   

if __name__ == '__main__':
    main()
