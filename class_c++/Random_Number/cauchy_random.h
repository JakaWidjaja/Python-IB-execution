#ifndef CAUCHY_RANDOM_H
#define CAUCHY_RANDOM_H

#include "random_number_generator.h"
#include "uniform_random_number.h"

class cauchy_random
{
public:
	//Constructor
	cauchy_random(uniform_random_number& uniform_number, const double& mu, const double& sigma);

	//Destructor
	virtual ~cauchy_random();

	virtual double generate_number();

private:
	uniform_random_number& uniform_number;
	const double& mu;
	const double& sigma;
};

	
#endif