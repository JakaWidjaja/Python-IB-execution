#include "cev_model.h"
#include "math.h"

//Constructor
cev_model::cev_model(const double& c_stock_price, const double& c_gamma, const double& c_sigma):
					stock_price(c_stock_price), gamma(c_gamma), sigma(c_sigma)
{}

//Destructor
cev_model::~cev_model()
{}

double cev_model::get_volatility()
{
	return sigma * pow(stock_price, (gamma - 2) / 2);
}