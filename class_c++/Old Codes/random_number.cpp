#include "random_number.h"
#include "random_number_generator.h"
#include "uniform_random_number.h"
 
//Constructor
random_number::random_number(uniform_random_number& c_uniform_generator, 
							 random_number& c_other_generator,
							 const unsigned long& c_seed):
							uniform_generator(c_uniform_generator),
							other_generator(c_other_generator),
							seed(c_seed)
{}

//Destructor
random_number::~random_number()
{}

double random_number::generate_number()
{}

//Generate uniform random number
double random_number::uniform_number()
{
	return uniform_generator.generate_number(seed);
}

double random_number::random()
{
	return other_generator.generate_number();
}