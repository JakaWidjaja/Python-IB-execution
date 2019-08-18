#ifndef LOGISTIC_RANDOM_H
#define LOGISTIC_RANDOM_H

/*
This is a random number generated from logistic distribution. 
*/

#include "random_number_generator.h"
#include "uniform_random_number.h"

class logistic_random: public random_number_generator
{
public:
	//Constructor
	logistic_random(uniform_random_number& uniform_number, const double& mu, const double& sigma);

	//Destructor
	virtual ~logistic_random();

	//Generate an logistic random number.
	virtual double generate_number();

private:
	uniform_random_number& uniform_number;
	const double& mu;
	const double& sigma;
};

#endif