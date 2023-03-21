#include <stdio.h>
#include <stdlib.h>

double samples[100];
int main(int argc, char *argv[])
{
	int i, j;
		
	for (i = 0; i < argc-1; i++) {
		FILE *f;

		f = fopen(argv[i+1], "r");
		for (j = 0; j < 10; j++) {
			int tmp;
			double s;
			
			fscanf(f, "%d %lf", &tmp, &s);
			samples[j] += s;
		}
	}

	for (i = 0; i < 10; i++)
		printf("%d %lf\n", i+1, samples[i]/(double)(argc-1));
}
