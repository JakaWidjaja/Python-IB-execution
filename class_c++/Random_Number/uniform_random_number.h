#ifndef UNIFORM_RANDOM_NUMBER_H
#define UNIFORM_RANDOM_NUMBER_H

class uniform_random_number
{
public:
	//Constructor
	uniform_random_number();

	//Destructor
	~uniform_random_number();

	virtual double generate_number(const unsigned long int& seed);
};

#endif