#include "garch.h"
#include <math.h>

//Constructor
garch::garch(const double& c_mean, const double& c_alpha_0, 
			 const double& c_alpha_1, const double& c_beta,
			 const double& c_lag_return, const double& c_lag_vol):
	mean(c_mean), alpha_0(c_alpha_0), alpha_1(c_alpha_1), 
	beta(c_beta), lag_return(c_lag_return), lag_vol(c_lag_vol)
{	
}

//Destructor
garch::~garch()
{
}


double garch::get_volatility(void)
{
	double sigma(0);
	double residual(0);

	//Calculate the residual.
	residual = lag_return - mean;

	sigma = sqrt(alpha_0 + (alpha_1 * residual * residual) + (beta * lag_vol * lag_vol));

	return sigma;
}

double garch::log_likelihood(const double& current_return)
{
	double log_garch(0);
	double residual(0);

	residual = current_return - mean;

	log_garch = -0.5 * log(this->get_volatility() * this->get_volatility()) - 
				 0.5 * ((residual * residual) / (this->get_volatility() * this->get_volatility()));

	return log_garch;
}
