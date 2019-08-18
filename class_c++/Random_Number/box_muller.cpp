#include "box_muller.h"
#include <math.h>

//Constructor
box_muller::box_muller(uniform_random_number& c_uniform_number, 
					   const double& c_mu, const double& c_sigma):
					   uniform_number (c_uniform_number), mu(c_mu), sigma(c_sigma)
{}

//Destructor
box_muller::~box_muller()
{}

double box_muller::generate_number()
{
	double v1;
	double v2;
	double rsq; 
	double fac;
	double store_val(0);

	if (store_val == 0.0)
	{
		do
		{
			v1 = 2.0 * uniform_number.generate_number() - 1.0;
			v2 = 2.0 * uniform_number.generate_number() - 1.0;
			rsq = v1 * v1 + v2 * v2;
		}while (rsq >= 1.0 || rsq == 0.0);

		fac = sqrt(-2.0 * log(rsq) / rsq);
		store_val = v1 * fac;
		return mu + sigma * v2 * fac;
	}
	else
	{
		fac = store_val;
		store_val = 0.0;
		return mu + sigma * fac;
	}
}