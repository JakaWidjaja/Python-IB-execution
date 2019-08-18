#ifndef POISSON_RANDOM_H
#define POISOON_RANDOM_H

#include "random_number_generator.h"

class poisson_random : public random_number_generator
{
public:
	//Constructor
	poisson_random();

	//Destructor
	virtual ~poisson_random();

	virtual double generate_number();

private:

};

#endif