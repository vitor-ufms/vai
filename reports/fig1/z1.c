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

double my_pareto(double a, double mean)
{
	double u = drand48();
    double x_m = mean * (1. - (1./a));
	double value = x_m / pow(u, (1./a));
	return value;
}

void gen_pareto(double *ev, int n, double a, double mean, long seed)
{
	int t = 0;
	double cur_t;
	
	srand48(seed);
	cur_t = 0;
	while (1) {
		cur_t += my_pareto(a, mean);
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

int main(int argc, char *argv[])
{
	int N, seed, i, n;
	double a, mean, *series, e;

	if (argc != 5) {
		fprintf(stderr, "Usage: z1 <N> <a> <mean> <seed>\n");
		exit(1);
	}
	N = atoi(argv[1]);
	a = atof(argv[2]);
	mean = atof(argv[3]);
	seed = atoi(argv[4]);
	series = Malloc(N * sizeof(double));

	// generate the series with exponential interarrival time
	gen_pareto(series, N, a,  mean, seed);

	n = N;
	for (i = 0; i < log2(N); i++) {
		e = energy(series, n);
		n = n / 2;
		printf("%d %lf\n", i+1, e);
	}
}
