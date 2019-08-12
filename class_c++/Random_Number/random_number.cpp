#include "random_number.h"
#include "random_number_generator.h"
#include "uniform_random_number.h"

//Constructor
random_number::random_number(uniform_random_number& c_uniform_generator,
							 random_number_generator& c_other_generator):
							other_generator(c_other_generator),
							uniform_generator(c_uniform_generator) 
{}

//Destructor
random_number::~random_number()
{}

double random_number::random(const unsigned long& seed)
{
	double uniform_number;

	uniform_number = uniform_generator.generate_number(seed);

	return other_generator.generate_number(uniform_number);
}