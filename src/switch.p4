/* -*- P4_16 -*- */
/* P4 program for a switch that uses a wavelet transform to detect periodicity */
/* Arthur Selle Jacobs (asjacobs@inf.ufrgs.br) */
/* INF-UFRGS / Princeton University Computer Science Department */

#include <core.p4>
#include <v1model.p4>

#include "includes/wavelets.p4"

/* ipv4 type header */
const bit<16> TYPE_IPV4 = 0x800;
/* tcp type header */
const bit<8> TYPE_TCP = 0x6;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

/* Ethernet header */
header ethernet_t {
  macAddr_t dstAddr;
  macAddr_t srcAddr;
  bit<16>   etherType;
}

/* ipv4 header */
header ipv4_t {
  bit<4>    version;
  bit<4>    ihl;
  bit<8>    diffserv;
  bit<16>   totalLen;
  bit<16>   identification;
  bit<3>    flags;
  bit<13>   fragOffset;
  bit<8>    ttl;
  bit<8>    protocol;
  bit<16>   hdrChecksum;
  ip4Addr_t srcAddr;
  ip4Addr_t dstAddr;
}

/* TCP Header */
header tcp_t {
  bit<16> srcPort;
  bit<16> dstPort;
  bit<32> seqNo;
  bit<32> ackNo;
  bit<4>  dataOffset;
  bit<3>  res;
  bit<3>  ecn;
  bit<1>  urg;
  bit<1>  ack;
  bit<1>  psh;
  bit<1>  rst;
  bit<1>  syn;
  bit<1>  fin;
  bit<16> window;
  bit<16> checksum;
  bit<16> urgentPtr;
}

struct metadata {

}


struct headers {
  ethernet_t  ethernet;
  ipv4_t      ipv4;
  tcp_t       tcp;
}


/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
        out headers hdr,
        inout metadata meta,
        inout standard_metadata_t standard_metadata) {
  state start {
    transition parse_ethernet;
  }

  /* parse ethernet header */
  state parse_ethernet {
    packet.extract(hdr.ethernet);
    transition select(hdr.ethernet.etherType) {
      TYPE_IPV4: parse_ipv4;
      default: accept;
    }
  }

  /* parse ipv4 header */
  state parse_ipv4 {
    packet.extract(hdr.ipv4);
    /* check to see if tcp packet */
    transition select(hdr.ipv4.protocol) {
      TYPE_TCP: parse_tcp;
      default: accept;
    }
  }

  /* parse tcp header */
  state parse_tcp {
    packet.extract(hdr.tcp);
    transition accept;
  }
}

/*************************************************************************
************   C H E C K S U M  V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
  apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/
control MyIngress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
  Wavelets() wavelets;

  action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
    standard_metadata.egress_spec = port;
    hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
    hdr.ethernet.dstAddr = dstAddr;
    hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
  }

  action drop() {
    mark_to_drop(standard_metadata);
  }

  table ipv4_lpm {
    key = {
      hdr.ipv4.dstAddr: lpm;
    }
    actions = {
      ipv4_forward;
      drop;
      NoAction;
    }
    size = 1024;
    default_action = drop();
  }
  
  apply {
    // TO-DO: just start when send a PCAP file o packets by scapy
    // if(hdr.tcp.dstPort == 1234){
    // }
    
    if (hdr.tcp.srcPort != 1234) {
      ipv4_lpm.apply();
      wavelets.apply(standard_metadata);
    }
  }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
         inout metadata meta,
         inout standard_metadata_t standard_metadata) {
  apply {  }
}

/*************************************************************************
*************   C H E C K S U M C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
  apply {
    update_checksum(
        hdr.ipv4.isValid(),
        { hdr.ipv4.version,
          hdr.ipv4.ihl,
          hdr.ipv4.diffserv,
          hdr.ipv4.totalLen,
          hdr.ipv4.identification,
          hdr.ipv4.flags,
          hdr.ipv4.fragOffset,
          hdr.ipv4.ttl,
          hdr.ipv4.protocol,
          hdr.ipv4.srcAddr,
          hdr.ipv4.dstAddr
        },
        hdr.ipv4.hdrChecksum,
        HashAlgorithm.csum16);
  }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
  apply {
    packet.emit(hdr.ethernet);
    packet.emit(hdr.ipv4);
    packet.emit(hdr.tcp);
  }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
  MyParser(),
  MyVerifyChecksum(),
  MyIngress(),
  MyEgress(),
  MyComputeChecksum(),
  MyDeparser()
) main;