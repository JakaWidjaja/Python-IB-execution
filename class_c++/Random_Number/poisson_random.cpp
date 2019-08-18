#include "poisson_random.h"

//Constructor
poisson_random::poisson_random(uniform_random_number& c_uniform_number, const double& c_lambda):
								uniform_number(c_uniform_number), lambda(c_lambda)
{}

//Destructor
poisson_random::~poisson_random()
{}

poisson_random::generate_number()
{
	int k;

	double u;
	double u2;
	double v;
	double v2;
	double p;
	double t;
	double lfac;

	double logfact[] = {1024, -1.0};

	if (lambda)
}