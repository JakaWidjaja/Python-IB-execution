#ifndef RANDOM_NUMBER_GENERATOR_H
#define RANDOM_NUMBER_GENERATOR_H

class random_number_generator
{
public:
	//Constructor
	random_number_generator();

	//Destructor
	~random_number_generator();

	virtual double generate_number(const double& uniform_number) = 0;
};

#endif