#include "exponential_random.h"
#include <math.h>

//Constructor
exponential_random::exponential_random(const double& c_beta): beta(c_beta)
{}

//Destructor
exponential_random::~exponential_random()
{}

double exponential_random::generate_number(const double& uniform_random_number)
{
	double u;

	if (uniform_random_number == 0.0)
	{
		return 0.0;
	}

	return -log(uniform_random_number) / beta;
}