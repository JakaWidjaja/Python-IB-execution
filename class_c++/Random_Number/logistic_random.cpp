#include "logistic_random.h"
#include "math.h"

//Constructor
logistic_random::logistic_random(uniform_random_number& c_uniform_number, 
								 const double& c_mu, const double& c_sigma):
								 uniform_number(c_uniform_number), mu(c_mu), sigma(c_sigma)
{}

//Destructor
logistic_random::~logistic_random()
{}

double logistic_random::generate_number()
{
	double u;

	u = uniform_number.generate_number();

	while(u * (1.0 - u) == 0.0)
	{
		u = uniform_number.generate_number();
	}

	return mu + 0.551328895421792050 * sigma * sigma * 
			log(u / (1 - u));
}