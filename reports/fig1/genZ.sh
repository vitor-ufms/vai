#/bin/bash
# ${2} = data size
# ${3} = epochs 
# ${4} = alpha 
# ${5} = mean 
# ${6} = directory 

rm -rf ${6}
mkdir ${6}
for i in $( seq 1 ${3})
do
    seed=$RANDOM
    ./${1} ${2} ${4} ${5} $seed > ${6}/${1}-$seed.txt
done

