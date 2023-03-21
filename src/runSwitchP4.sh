#!/bin/bash

echo '#############################################'
echo '###### Deteniendo procesos anteriores #######'
echo '#############################################'  
make stop
echo '#############################################'
echo '###### Limpiando procesos anteriores ########'
echo '#############################################'
make clean
part="$1"
line="$2" 
init1Line=$((139))
last1Line=$((169))
init2Line=$((174))
last2Line=$((205))
if [ "$part" -eq 0 ];then
    sed -i "$init1Line,$last1Line s/\/\///g" includes/squares.p4
    sed -i "$init1Line,$last1Line s/^/\/\//" includes/squares.p4
    sed -i "$init2Line,$last2Line s/\/\///g" includes/squares.p4
    sed -i "$init2Line,$last2Line s/^/\/\//" includes/squares.p4
    echo '#############################################'
    echo '######### Ejecutar proceso en P4 ############'
    echo '#############################################'
    make run
elif [ "$part" -eq 1 ];then
    readLine=$(($2+$init1Line-1))
    nextLine=$(($2+$init1Line))
    echo "#############################################"
    echo "############ StepAlign Line: $2 #############"
    echo "#############################################"
    if [ "$readLine" == "$init1Line" ];then
        sed -i "$init1Line s/\/\///g" includes/squares.p4
        sed -i "$nextLine,$last1Line s/\/\///g" includes/squares.p4
        sed -i "$nextLine,$last1Line s/^/\/\//" includes/squares.p4
        sed -i "$init2Line,$last2Line s/\/\///g" includes/squares.p4
        sed -i "$init2Line,$last2Line s/^/\/\//" includes/squares.p4
        echo '#############################################'
        echo '######### Ejecutar proceso en P4 ############'
        echo '#############################################'
        make run
    elif [ "$readLine" == "$last1Line" ];then
        sed -i "$init1Line,$last1Line s/\/\///g" includes/squares.p4
        sed -i "$init2Line,$last2Line s/\/\///g" includes/squares.p4
        sed -i "$init2Line,$last2Line s/^/\/\//" includes/squares.p4
        echo '#############################################'
        echo '######### Ejecutar proceso en P4 ############'
        echo '#############################################'
        make run
    elif [ "$readLine" -gt "$init1Line" -a "$readLine" -lt "$last1Line" ];then
        sed -i "$init1Line,$readLine s/\/\///g" includes/squares.p4
        sed -i "$nextLine,$last1Line s/\/\///g" includes/squares.p4
        sed -i "$nextLine,$last1Line s/^/\/\//" includes/squares.p4
        sed -i "$init2Line,$last2Line s/\/\///g" includes/squares.p4
        sed -i "$init2Line,$last2Line s/^/\/\//" includes/squares.p4
        echo '#############################################'
        echo '######### Ejecutar proceso en P4 ############'
        echo '#############################################'
        make run
    else
        echo 'Linea fuera de rango'
    fi
elif [ "$part" -eq 2 ];then
    readLine=$(($2+$init2Line-1))
    nextLine=$(($2+$init2Line))
    echo "#############################################"
    echo "############ DivideStep Line: $2 ############"
    echo "#############################################"
    if [ "$readLine" == "$init2Line" ];then
        sed -i "$init1Line,$last1Line s/\/\///g" includes/squares.p4
        sed -i "$init2Line s/\/\///g" includes/squares.p4
        sed -i "$nextLine,$last2Line s/\/\///g" includes/squares.p4
        sed -i "$nextLine,$last2Line s/^/\/\//" includes/squares.p4
        echo '#############################################'
        echo '######### Ejecutar proceso en P4 ############'
        echo '#############################################'
        make run
    elif [ "$readLine" == "$last2Line" ];then
        sed -i "$init1Line,$last1Line s/\/\///g" includes/squares.p4
        sed -i "$init2Line,$last2Line s/\/\///g" includes/squares.p4
        echo '#############################################'
        echo '######### Ejecutar proceso en P4 ############'
        echo '#############################################'
        make run
    elif [ "$readLine" -gt "$init2Line" -a "$readLine" -lt "$last2Line" ];then
        sed -i "$init1Line,$last1Line s/\/\///g" includes/squares.p4
        sed -i "$init2Line,$readLine s/\/\///g" includes/squares.p4
        sed -i "$nextLine,$last2Line s/\/\///g" includes/squares.p4
        sed -i "$nextLine,$last2Line s/^/\/\//" includes/squares.p4
        echo '#############################################'
        echo '######### Ejecutar proceso en P4 ############'
        echo '#############################################'
        make run
    else
        echo 'Linea fuera de rango'
    fi
elif [ "$part" -eq 3 ];then
    sed -i "$init1Line,$last1Line s/\/\///g" includes/squares.p4
    sed -i "$init2Line,$last2Line s/\/\///g" includes/squares.p4
    echo '#############################################'
    echo '######### Ejecutar proceso en P4 ############'
    echo '#############################################'
    make run
fi
