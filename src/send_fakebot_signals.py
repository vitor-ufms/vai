#!/usr/bin/env python
import argparse
import sys, getopt
import socket
import random
import struct
import time
import os

from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP

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
    duration = 1.

    if len(sys.argv)<2:
        print 'Need arguments'
        exit(1)

    # tcpreplay -T nano --pktlen -i eth0 ../utils/pcap/trickbot_split15min.pcap

    type_signals    = sys.argv[1]
    if (type_signals == "N"):
        num_packets = sys.argv[2] 
        num_seconds_sleep = sys.argv[3] 
        cli = "tcpreplay -T nano --pktlen -i eth0  ../utils/pcap/fakebot_" + num_packets + "pp" + num_seconds_sleep + "s_5min.pcap" 
        cli = cli + " & "
        num_packets = sys.argv[4] 
        num_seconds_sleep = sys.argv[5] 
        cli = cli + "tcpreplay -T nano --pktlen -i eth0  ../utils/pcap/fakebot_" + num_packets + "pp" + num_seconds_sleep + "s_5min.pcap"

    elif(type_signals == "B"):
        filename1 = sys.argv[2]
        cli = "tcpreplay -T nano --pktlen -i eth0  ../utils/pcap/" + filename1 + ".pcap"
        cli = cli + " & "
        filename2 = sys.argv[3]  
        cli = cli + "tcpreplay -T nano --pktlen -i eth0  ../utils/pcap/" + filename2 + ".pcap"
    elif(type_signals == "F"):
        filename = sys.argv[2]
        cli = "tcpreplay -T nano --pktlen -i eth0  ../utils/pcap/" + filename + ".pcap"
        cli = cli + " & "
        cli = cli + "tcpreplay -T nano --pktlen -i eth0  ../utils/pcap/lbl-internal.20041004-1303.port001.dump.anon"

    print(cli)
    os.system(cli)
    finish_ring()

   

if __name__ == '__main__':
    main()
