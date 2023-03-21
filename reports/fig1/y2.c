#include <time.h>
#include <math.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void unix_error(char *msg)
{
	fprintf(stderr, "%s: %s\n", msg, strerror(errno));
	exit(1);
}

void *Malloc(size_t memsize)
{
	void *p = calloc(1, memsize);

	if (!p)
		unix_error("malloc");
	return p;
}

double my_exp(double mean)
{
	double u = drand48(); // (double)random() / RAND_MAX;
	return -mean*log(u);
}

void gen_exp(double *ev, int n, double mean, long seed)
{
	int t = 0;
	double cur_t;
	
	srand48(seed);
	cur_t = 0;
	while (1) {
		cur_t += my_exp(mean);
		t = floor(cur_t);
		if (t < n)
			ev[t]++;
		else
			break;
	}
}

double energy(double *X, int n)
{
	int k;
	double sum = 0, dj;
	
	for (k = 0; k < n/2; k++) {
		dj = (X[2 * k] - X[2 * k + 1]) / sqrt(2.);
		sum += dj * dj;
		X[k] = (X[2 * k] + X[2 * k + 1]) / sqrt(2.);
	}
	n = n / 2;
	sum = sum / n;
	if (sum < 0.000000001)
		return 0.;
	
	return log2(sum);
}

void gen_quarter(double *ev, int n, int seed)
{
	int q1, i, j, N, x;
	int *ones;

	ones = Malloc(n*sizeof(int));
	N = 0;
	for (i = 0; i < n; i++)
		if (ev[i] > 0.)
			ones[N++] = i;
	q1 = N / 4;	
	srand(seed);
	i = 0;
	while (1) {
		j = rand() % N; // select a sample
		if (ones[j]) {
			x = ones[j] + 8;		
			if (x < n) {
				ev[x]++;
				ones[j] = 0;
				if (++i >= q1)
					break;
			}
		}
	}

	i = 0;
	while (1) {
		j = rand() % N; // select a sample
		if (ones[j]) {
			x = ones[j] + 18;
			if (x < n) {
				ev[x]++;
				ones[j] = 0;
				if (++i >= q1)
					break;
			}
		}
	}
}

int main(int argc, char *argv[])
{
	int N, seed, i, n;
	double mean, *series, e;

	if (argc != 4) {
		fprintf(stderr, "Usage: y2 <N> <mean> <seed>\n");
		exit(1);
	}
	N = atoi(argv[1]);
	mean = atof(argv[2]);
	seed = atoi(argv[3]);
	series = Malloc(N * sizeof(double));

	// generate the series with exponential interarrival time
	gen_exp(series, N, mean, seed);

	// pick a quarter randomly and add 1 at r+8 and r+18
	gen_quarter(series, N, seed);
	
	n = N;
	for (i = 0; i < log2(N); i++) {
		e = energy(series, n);
		n = n / 2;
		printf("%d %lf\n", i+1, e);
	}
}
