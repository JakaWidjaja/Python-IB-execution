#include "market_implied.h"

//Constructor
market_implied::market_implied(const double& c_imp_vol): imp_vol(c_imp_vol)
{
}

//Destructor
market_implied::~market_implied()
{}

double market_implied::get_volatility()
{
	return imp_vol;
}