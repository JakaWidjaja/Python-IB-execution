#ifndef RANDOM_NUMBER_H
#define RANDOM_NUMBER_H

#include "random_number_generator.h"
#include "uniform_random_number.h"

class random_number
{
public:
	//Constructor
	//uniform_generator is the class for uniform generator either pseudo or quasi. 
	//Generator is the other non-uniforem random number generator. 
	random_number(uniform_random_number& uniform_generator, random_number& other_generator,
					const unsigned long& seed);

	//Destructor
	~random_number();

	virtual double generate_number();

	//generate uniform random number
	virtual double uniform_number();

	double random();

private:
	uniform_random_number& uniform_generator;
	random_number& other_generator;
	const unsigned long& seed;
};

#endif