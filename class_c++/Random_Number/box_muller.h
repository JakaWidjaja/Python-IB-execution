#ifndef BOX_MULLER_H
#define BOX_MULLER_H

/*
This is a random number generated from normal distribution using Box Muller method. 
*/

#include "random_number_generator.h"
#include "uniform_random_number.h"

class box_muller: public random_number_generator
{
public:
	//Constructor
	box_muller(uniform_random_number& uniform_number, const double& mu, const double& sigma);

	//Destructor
	virtual ~box_muller();

	//Generate an normal random number.
	virtual double generate_number();

private:
	uniform_random_number& uniform_number;
	const double& mu;
	const double& sigma;
};

#endif