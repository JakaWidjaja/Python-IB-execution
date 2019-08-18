#ifndef EXPONENTIAL_RANDOM_H
#define EXPONENTIAL_RANDOM_H

/*
This is a random number generated from exponential distribution. 
*/

#include "random_number_generator.h"
#include "uniform_random_number.h"

class exponential_random: public random_number_generator
{
public:
	//Constructor
	exponential_random(uniform_random_number& uniform_number, const double& beta);

	//Destructor
	virtual ~exponential_random();

	//Generate an exponential random number between 0 and 1
	virtual double generate_number();

private:
	const double& beta;
	uniform_random_number& uniform_number;
};

#endif