#include "exponential_random.h"
#include <math.h>

//Constructor
exponential_random::exponential_random(uniform_random_number& c_uniform_number, const double& c_beta): 
										beta(c_beta), 
										uniform_number(c_uniform_number)
{
}

//Destructor
exponential_random::~exponential_random()
{}

double exponential_random::generate_number()
{
	double u;

	u = uniform_number.generate_number();

	while (u == 0.0)
	{
		u = uniform_number.generate_number();
	}

	return -log(u) / beta;
}