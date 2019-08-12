#include "garchm.h"
#include <math.h>

//Constructor
garchm::garchm(const double& c_mean, const double& c_c, 
			   const double& c_alpha_0, const double& c_alpha_1, 
			   const double& c_beta, const double& c_lag_return,
		       const double& c_lag_vol):
	mean(c_mean), c(c_c), alpha_0(c_alpha_0), alpha_1(c_alpha_1), 
	beta(c_beta), lag_return(c_lag_return), lag_vol(c_lag_vol)
{
}

//Destructor
garchm::~garchm()
{}

double garchm::sigma_t(const int& type)
{
	double sigma(0);
	double residual(0);

	if (type == 1)
	{
		residual = lag_return - *mean - (c * lag_vol * lag_vol);
	}
	else if (type == 2)
	{
		residual = lag_return - mean - (c * lag_vol);
	} 
	else if(type == 3)
	{
		residual = lag_return - mean - (c * log(lag_vol) * lag_vol);
	}

	sigma = sqrt(alpha_0 + (alpha_1 * residual * residual) + (beta * lag_vol * lag_vol));

	return sigma;
}

double garchm::log_likelihood(const double& current_return)
{
	double log_igarch(0);
	double residual(0);

	residual = current_return - mean;

	log_igarch = -0.5 * log(this->get_volatility() * this->get_volatility())
				-0.5 * ((residual * residual) / (this->get_volatility() * this->get_volatility()));

	return log_igarch;
}
