
set yrange [-5.2:2.0]
set ytics -5,1
set xrange [0:11]
set xlabel "Scale j"
set ylabel "log2(Energey(j))"
set key left top
set terminal pngcairo enhanced font "Times New Roman,12.0" 
set output "Figure2.png" 
plot "z1-data/z1avg100-128k.txt" w linespoints title "Z1", "z2-data/z2avg100-128k.txt" w linespoints title " Z2" 