#ifndef MARKET_CORRELATION
#define MARKET_CORRELATION

#include "correlation.h"

class market_correlation: public correlation
{
public:
	//Constructor
	market_correlation(const double& correl);

	//Destructor
	~market_correlation();

	virtual double get_correlation();

private:
	const double& correl;
};

#endif