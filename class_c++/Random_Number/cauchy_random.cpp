#include "cauchy_random.h"

//Constructor
cauchy_random::cauchy_random(uniform_random_number& c_uniform_number, 
					   		 const double& c_mu, const double& c_sigma):
					   		 uniform_number (c_uniform_number), mu(c_mu), sigma(c_sigma)
{}

//Destructor
cauchy_random::~cauchy_random()
{}

double cauchy_random::generate_number()
{
	double v1;
	double v2;

	do 
	{
		v1 = 2.0 * uniform_number.generate_number() - 1.0;
		v2 = uniform_number.generate_number();
	}while((v1 * v1 + v2 * v2) >= 1.0 || v2 == 0.0);

	return mu + sigma * v1 / v2;
}