#ifndef MARKET_IMPLIED_H
#define MARKET_IMPLIED_H

#include "volatility.h"

/*
This class purpose is to only take the market implied volatility.
There is no calculation done. 
*/
class market_implied : public volatility
{
public:
	//Contructor
	market_implied(const double& imp_vol);
	
	//Destructor
	~market_implied();

	virtual double get_volatility();

private:
	const double& imp_vol;
};

#endif