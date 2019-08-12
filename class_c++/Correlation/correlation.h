#ifndef CORRELATION_H
#define CORRELATION_H

/*
Abstract base class
*/
class correlation
{
public:
	//Constructor
	correlation();

	//Destructor
	~correlation();

	//A simple correlation. e.g. calibrated from the model.
	virtual double get_correlation() = 0;
};


#endif