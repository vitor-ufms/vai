size = 131072
epochs = 100


gen: y1 y2 z1 z2 avg

y1: y1.c
	gcc y1.c -o y1 -lm

y2: y2.c
	gcc y2.c -o y2 -lm

z1: z1.c
	gcc z1.c -o z1 -lm

z2: z2.c
	gcc z2.c -o z2 -lm

avg: avg.c
	gcc avg.c -o avg -lm


run:	
	bash genY.sh y1 $(size) $(epochs) 10 y1-data
	bash genY.sh y2 $(size) $(epochs) 15 y2-data

	bash genDataFiles.sh y1 y1-data $(epochs) 128k
	bash genDataFiles.sh y2 y2-data $(epochs) 128k

	bash genZ.sh z1 $(size) $(epochs) 1.2 10.0 z1-data
	bash genZ.sh z2 $(size) $(epochs) 1.2 10.0 z2-data

	bash genDataFiles.sh z1 z1-data $(epochs) 128k
	bash genDataFiles.sh z2 z2-data $(epochs) 128k

	gnuplot Figure1.gnuplot
	gnuplot Figure2.gnuplot


clean:
	rm -rf *~ y1 y2 z1 z2 avg y1-data y2-data z1-data z2-data

