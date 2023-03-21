DIRPATH="../utils/pcap/"
namePCAP="100.pcap"
iface="eth0"
num_kts=100
inter_pkts=1
slot_duration=5
total_slots=230

cli="./pkt_gen ${DIRPATH}${namePCAP} ${iface} ${num_kts} ${inter_pkts} ${slot_duration} ${total_slots}"

echo "${cli}"
eval $cli
