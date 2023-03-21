#!/usr/bin/env python
import argparse
import sys
import os
import socket
import time
import random
import ctypes

import progressbar
from progress.bar import Bar

from scapy.all import sniff, rdpcap
from scapy.all import sendp, sendrecv, wrpcap, sendpfast
from scapy.all import get_if_list, get_if_hwaddr
from scapy.all import Ether, IP, UDP, TCP

libc = ctypes.CDLL('libc.so.6')
filepath = '../utils/pcap/trickbot.pcap'

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

def count_packets_per_second(pkts):
    cntPktsPerSecond = {}
    count, start, end = 0,0,0
    for pkt in pkts:
        if count == 0:
            start = int(pkt.time)
        end = int(pkt.time)
        count += 1

        key = int(pkt.time)
        if key not in cntPktsPerSecond:
            cntPktsPerSecond[key] = 0
        cntPktsPerSecond[key] += 1
        
    return cntPktsPerSecond, start, end



def send_packet_per_second(addr, iface, pkts, number_packets):

    start   = int(pkts[0].time)
    end     = int(pkts[-1].time)
    time_send = end +1 - start

    with Bar('Processing...', max=(time_send)) as bar:

        # number_total_packets = number_packets * time_send
        number_total_packets = number_packets * 7209

        print '################################'
        print "sending on interface %s to %s" % (iface, str(addr))
        
        pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt /IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / sys.argv[2]

        inter = 1./float(number_total_packets)
        print str(number_total_packets)
        print str(inter)
        sendp(pkt, iface=iface, verbose=False, count = number_total_packets, inter = inter, loop = 1)
        # sendpfast(pkt, iface=iface, pps = number_packets)

        print '################################'
        bar.next()
        bar.finish()



def main():

    # python send_number_packets_in_second.py 10.0.2.2 'Hi' 10

    print '################################'
    print '## Get packets from PCAP File ##'
    print '################################'
    pkts = rdpcap(filepath)
    number_packets = int(sys.argv[3])
    
    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()


    print '################################'
    print '######### Send packets #########'
    print '################################'
    print '######### PPS: ' + str(number_packets) + ' #########'


    send_packet_per_second(addr, iface, pkts, number_packets)

    # Ring when the process finish 
    duration = 2
    freq = 2500
    os.system('play -nq -t alsa synth {} sine {}'.format(duration,freq))
    os.system('spd-say "Your program has finished"') 

if __name__ == '__main__':
    main()