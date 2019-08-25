#ifndef CEV_MODEL_H
#define CEV_MODEL_H

#include "volatility.h"

class cev_model : public volatility
{
public:
	//Constructor
	cev_model(const double& stock_price, const double& gamma, const double& sigma);

	//Destructor
	virtual ~cev_model();

	virtual double get_volatility();

private:
	const double& stock_price;
	const double& gamma; //This is the constant parameter. 
	const double& sigma; //This is the volatility of volatility.

};

#endif