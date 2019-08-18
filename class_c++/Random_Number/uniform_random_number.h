#ifndef UNIFORM_RANDOM_NUMBER_H
#define UNIFORM_RANDOM_NUMBER_H

class uniform_random_number
{
public:
	//Constructor
	uniform_random_number();

	//Destructor
	virtual ~uniform_random_number();

	virtual double generate_number() = 0;
};

#endif