#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/time.h>
#include <pcap/pcap.h>
#include <arpa/inet.h>

#define SecToNano(x)	((x)*1000000000LL)
#define SecToMicro(x)	((x)*1000000LL)
#define SecToMilli(x)	((x)*1000LL)

#define MilliToMicro(x) ((x)*1000LL)
#define MilliToNano(x)  ((x)*1000000LL)

#define MicroToNano(x)	((x)*1000LL)

#define BUFFER_SIZE 1500

#define SIZE_ETHERNET 14

/* IP header */
struct sniff_ip {
	u_char ip_vhl;		/* version << 4 | header length >> 2 */
	u_char ip_tos;		/* type of service */
	u_short ip_len;		/* total length */
	u_short ip_id;		/* identification */
	u_short ip_off;		/* fragment offset field */
#define IP_RF 0x8000		/* reserved fragment flag */
#define IP_DF 0x4000		/* dont fragment flag */
#define IP_MF 0x2000		/* more fragments flag */
#define IP_OFFMASK 0x1fff	/* mask for fragmenting bits */
	u_char ip_ttl;		/* time to live */
	u_char ip_p;		/* protocol */
	u_short ip_sum;		/* checksum */
	struct in_addr ip_src,ip_dst; /* source and dest address */
} __attribute__((__packed__));


typedef long long my_time_t;

u_char packet[BUFFER_SIZE];
int packet_size;

// return time of day in microseconds
long long now()
{
	struct timeval current_time;
  
	gettimeofday(&current_time, NULL);
	return SecToMicro(current_time.tv_sec) + current_time.tv_usec;
}

// interval is in microseconds
void my_sleep(long long interval)
{
	long x, start_time, elapsed;
	
	if (interval < 0)
		return;
	x = interval;
	start_time = now();
	while (1) {
		usleep(x);
		elapsed = now() - start_time;
		if (elapsed >= interval)
			break;
		x = interval - elapsed;
	}
}

void send_pkt(pcap_t *pcap_handle)
{
	printf("Sending packet\n");
	pcap_inject(pcap_handle, packet, packet_size);
}

// intf: interface name (eth0)
// pkts_per_slot: number of packets to send in a slot (slot is one second, so it is the number of packet to send in one second)
// packet_interval in milliseconds: use 1 millisecond, so you don't overload the P4 switch
// slot_duration in seconds: we are using one second
// total_slots: number of bins that we want to capture in the switch (i.e., number of seconds to send packets)
void send_throttled_packets(char *intf, int pkts_per_slot, int packet_interval, int slot_duration, int total_slots)
{
	my_time_t start_time, next_time, cur_time;	
	int i, j;
	pcap_t *pcap_handle;
	char err_buf[PCAP_ERRBUF_SIZE];

	pcap_handle = pcap_open_live(intf, BUFFER_SIZE, 1, 10000, err_buf);
	if (pcap_handle == NULL) {
		fprintf(stderr, "Error opening network interface %s\n", intf);
		exit(1);
	}
	start_time = now();
	next_time = start_time + MilliToMicro(packet_interval);
	for (i = 0; i < total_slots; i++) {
		cur_time = now();
		printf("Starting slot %d at %lf\n", i, cur_time/1000000.);
		for (j = 0; j < pkts_per_slot; j++) {
			send_pkt(pcap_handle);
			my_sleep(MilliToMicro(packet_interval));
		}
		cur_time = now();
		next_time = next_time + SecToMicro(slot_duration);
		if (cur_time < next_time) 
			my_sleep(next_time - cur_time);
	}
	pcap_close(pcap_handle);
}

void get_one_packet_from_pcap_file(char *input_file)
{
	char error_buffer[PCAP_ERRBUF_SIZE];
	pcap_t *handle;
	struct pcap_pkthdr header;
	struct bpf_program filter;
	char filter_exp[] = "ip or ip6";
	const u_char *pkt;
	
	handle = pcap_open_offline(input_file, error_buffer);
	if (handle == NULL) {
		fprintf(stderr, "Error opening pcap file %s\n", input_file);
		exit(1);
	}
	if (pcap_compile(handle, &filter, filter_exp, 0, PCAP_NETMASK_UNKNOWN) == -1) {
		fprintf(stderr, "Bad filter %s\n", pcap_geterr(handle));
		exit(1);
	}

	if ((pkt = pcap_next(handle, &header)) != NULL) {
		struct sniff_ip *ip;
		
		memcpy(packet, pkt, BUFFER_SIZE);
		pcap_close(handle);
		ip = (struct sniff_ip*)(packet+SIZE_ETHERNET);
		packet_size = SIZE_ETHERNET + ntohs(ip->ip_len);
		printf("Packet size %d\n", packet_size);
	}
	else {
		fprintf(stderr, "Error reading the packet from the file\n");
		exit(1);
	}
}

int main(int argc, char *argv[])
{
	char *pcap_file, *iface;
	int pkts_per_slot, packet_interval, slot_duration, total_slots;
	
	if (argc != 7) {
		fprintf(stderr, "Usage: pkt_gen pcap_file iface pkts_per_slot packet_interval slot_duration total_slots\n");
		exit(1);
	}
	pcap_file       = argv[1];
	iface           = argv[2];
	pkts_per_slot   = atoi(argv[3]);
	packet_interval = atoi(argv[4]);
	slot_duration   = atoi(argv[5]);
	total_slots     = atoi(argv[6]);

	get_one_packet_from_pcap_file(pcap_file);
	send_throttled_packets(iface, pkts_per_slot, packet_interval, slot_duration, total_slots);
}
