#ifndef SIMPSONS_H
#define SIMPSONS_H

#include "numerical_integration.h"

template<class T>
class simpsons: public numerical_integration<T>
{
public:
	//Constructor
	simpsons(const double& lower_bound, const double& upper_bound,
			 const int& interval);

	//Destructor
	virtual ~simpsons();

	virtual double integrate(T* func);

private:
	const double& lower_bound;
	const double& upper_bound;
	const int& interval;
};


#endif