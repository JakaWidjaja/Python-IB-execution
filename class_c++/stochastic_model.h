#ifndef STOCHASTIC_MODEL_H
#define STOCHASTIC_MODEL_H

//Abstract base class
class stochastic_model
{
public:
	//Constructor
	stochastic_model();

	//Destructor
	~stochastic_model();

	virtual double call_price() = 0;
};


#endif