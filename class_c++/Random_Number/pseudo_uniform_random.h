#ifndef PSEUDO_UNIFORM_RANDOM_H
#define PSEUDO_UNIFORM_RANDOM_H

#include "uniform_random_number.h"

/*
This method to generate uniform random number is taken from
Numerical Recipes 2007 page 351.
*/

class pseudo_uniform_random: public uniform_random_number
{
public:
	//Constructor
	pseudo_uniform_random();

	//Destructor
	~pseudo_uniform_random();

	//Generate uniform random number between 0 and 1
	virtual double generate_number(const unsigned long int& seed);

private:
	unsigned long long int v;

};

#endif