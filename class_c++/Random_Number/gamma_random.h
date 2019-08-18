#ifndef GAMMA_RANDOM_H
#define GAMMA_RANDOM_H

#include "random_number_generator.h"
#include "uniform_random_number.h"

class gamma_random : public random_number_generator 
{
public:
	//Constructor
	gamma_random(uniform_random_number& uniform_number, 
				double& alpha, const double& beta);

	//Destructor
	virtual ~gamma_random();

	virtual double generate_number();

private:
	uniform_random_number& uniform_number;
	double& alpha;
	const double& beta;
};

	
#endif