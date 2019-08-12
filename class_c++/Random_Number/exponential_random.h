#ifndef EXPONENTIAL_RANDOM_H
#define EXPONENTIAL_RANDOM_H

#include "random_number_generator.h"

class exponential_random: public random_number_generator
{
public:
	//Constructor
	exponential_random(const double& beta);

	//Destructor
	~exponential_random();

	//Generate an exponential random number between 0 and 1
	virtual double generate_number(const double& uniform_random_number);

private:
	const double& beta;
};

#endif