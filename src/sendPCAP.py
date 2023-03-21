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
filepath = '../utils/pcap/trickbot_split30min.pcap'

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

def sendPacketWithDelay(addr,iface,timeDelay,pktsTime):
    timePktPrevius = -1.
    timePktCurrent = 0.0

    with Bar('Processing...', max=len(pktsTime)) as bar:

        for pktTime in pktsTime:
            timePktCurrent = pktTime
            timeSleep = 0.0
            print '################################'
            print 'Tiempo Previo:'+str(timePktPrevius)
            print 'Tiempo Actual:'+str(timePktCurrent)
            if (timePktPrevius > 0.):
                timeSleep = timePktCurrent - timePktPrevius
                # # if(timeSleep > timeDelay ):
                # #     timeSleepMicroSeg = int((timeSleep-timeDelay) * 800000)
                # #     print 'Sleep: ' + str(timeSleepMicroSeg) + 'us, '+ str(timeSleep) + 's'
                # #     libc.usleep(timeSleepMicroSeg)
                # timeSleepMicroSeg = int((timeSleep) * 1000000)
                # print 'Sleep: ' + str(timeSleepMicroSeg) + 'us, '+ str(timeSleep) + 's'
                # libc.usleep(timeSleepMicroSeg)
                print str(timeSleep) + 's'
                time.sleep(timeSleep)
                
            pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
            pkt = pkt /IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / sys.argv[2]
            sendp(pkt, iface=iface, verbose=False)
            print '################################'
            timePktPrevius = pktTime
            bar.next()
        bar.finish()

def sendPacket(addr, iface, timeDelay, cntPkts, start, end):

    with Bar('Processing...', max=(end +1 - start)) as bar:

        for key in range(start, end +1):
            print '################################'
            print "sending on interface %s to %s" % (iface, str(addr))
            if key not in cntPkts:
                # time.sleep(1-timeDelay)
                time.sleep(1)
                print(key,' -> ',0)
            else:
                pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
                pkt = pkt /IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / sys.argv[2]
                # pkt.show2()
                # inter = (1. - timeDelay)/cntPkts[key]
                inter = (1.)/cntPkts[key]
                sendp(pkt, iface=iface, verbose=False, count = cntPkts[key], inter = inter )
                # sendpfast(pkt, iface=iface, pps = cntPkts[key], loop = cntPkts[key])
                print(key,' -> ',cntPkts[key])
            print '################################'
            bar.next()
        bar.finish()



def main():

    # if len(sys.argv)<2:
    #     print 'pass 2 arguments: <destination> "<message>"'
    #     exit(1)

    tsStart = 1572546230.
    tsEnd   = 1572552044.
    timeDelay = 0.021276596
    print '################################'
    print '## Get packets from PCAP File ##'
    print '################################'
    pkts = rdpcap(filepath)    
    
    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    print '################################'
    print '######### Send packets #########'
    print '################################'

    # python sendPCAP.py 10.0.2.2 'Hi' "-d" -> Packet forwarding with delay between them 
    # python sendPCAP.py 10.0.2.2 'Hi' "-"  -> Packet forwarding with packet count by second       
    if(sys.argv[3] == "-d"):
        pktsTime = list(map(lambda t :t.time, pkts))
        sendPacketWithDelay(addr, iface, timeDelay , pktsTime)
    else:
        start, end = 0,0
        cntPkts, start, end = count_packets_per_second(pkts)
        sendPacket(addr, iface, timeDelay, cntPkts, int(tsStart), int(tsEnd))

    # Ring when the process finish 
    duration = 2
    freq = 2500
    os.system('play -nq -t alsa synth {} sine {}'.format(duration,freq))
    os.system('spd-say "Your program has finished"') 

if __name__ == '__main__':
    main()