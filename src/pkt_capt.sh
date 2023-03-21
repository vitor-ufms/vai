DIRPATH="../utils/pcap/"
testname="trickbot"
testtype="30min"
ver=03
access=${1}

cli="tcpdump -n -i eth0 not src port 1234 -w ${DIRPATH}"
filename="${testname}_${testtype}_${ver}_${access}.pcap"
cli="${cli}${filename}"

echo "${cli}"
eval $cli
