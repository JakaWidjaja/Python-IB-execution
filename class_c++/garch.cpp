#include "garch.h"
#include <math.h>

//Constructor
garch::garch(const double* const c_mean, const double* const c_alpha_0, 
			 const double* const c_alpha_1, const double* const c_beta,
			 const double* const c_lag_return, const double* const c_lag_vol)
{	
	mean = c_mean;
	alpha_0 = c_alpha_0;
	alpha_1 = c_alpha_1;
	beta = c_beta;
	lag_return = c_lag_return;
	lag_vol = c_lag_vol;
}

//Destructor
garch::~garch()
{

}


double garch::sigma_t(void)
{
	
	double sigma(0);
	double residual(0);

	//Calculate the residual.
	residual = *lag_return - *mean;

	sigma = sqrt(*alpha_0 + (*alpha_1 * residual * residual) + (*beta * *lag_vol * *lag_vol));

	return sigma;
}

double garch::log_likelihood(const double* const current_return)
{
	double log_garch(0);
	double residual(0);

	residual = *current_return - *mean;

	log_garch = -0.5 * log(this-> sigma_t() * this -> sigma_t()) - 
				 0.5 * ((residual * residual) / (this -> sigma_t() * this -> sigma_t()));

	return log_garch;
}
