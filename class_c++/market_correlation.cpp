#include "market_correlation.h"

//Constructor
market_correlation::market_correlation(const double& correl): correl(0)
{

}

//Destructor
market_correlation::~market_correlation()
{}

double market_correlation::get_correlation()
{
	return correl;
}