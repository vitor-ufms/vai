#/bin/bash
# ${2} = data size
# ${3} = epochs 
# ${4} = mean 
# ${5} = directory 

rm -rf ${5}
mkdir ${5}
for i in $( seq 1 ${3})
do
    seed=$RANDOM
    ./${1} ${2} ${4} $seed > ${5}/${1}-$seed.txt
done

