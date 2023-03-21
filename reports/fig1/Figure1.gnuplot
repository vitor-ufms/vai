
set yrange [-5.5:2.0]
set ytics -5,1
set xrange [0:11]
set xlabel "Scale j"
set ylabel "log2(Energey(j))"
set terminal pngcairo enhanced font "Times New Roman,12.0" 
set output "Figure1.png" 
plot "y1-data/y1avg100-128k.txt" w linespoints title "Y1", "y2-data/y2avg100-128k.txt" w linespoints title "Y2" 