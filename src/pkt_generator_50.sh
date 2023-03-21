DIRPATH="../utils/pcap/"
namePCAP="50.pcap"
iface="eth0"
num_kts=50
inter_pkts=1
slot_duration=4
total_slots=530

cli="./pkt_gen ${DIRPATH}${namePCAP} ${iface} ${num_kts} ${inter_pkts} ${slot_duration} ${total_slots}"

echo "${cli}"
eval $cli
