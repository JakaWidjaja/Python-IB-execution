#include "igarch.h"
#include <math.h>

//Constructor
igarch::igarch(const double* c_mean, const double* c_alpha_0,
		       const double* c_beta, const double* c_lag_return, 
		       const double* c_lag_vol)
{
	mean = c_mean;
	alpha_0 = c_alpha_0;
	beta = c_beta;
	lag_return = c_lag_return;
	lag_vol = c_lag_vol;
}

//Destructor
igarch::~igarch()
{}

double igarch::sigma_t()
{
	double sigma(0);
	double residual(0);

	//Calculate the residual
	residual = *lag_return - *mean;

	sigma = sqrt(*alpha_0 + *beta * (*lag_vol) * (*lag_vol) + (1 - *beta) * (residual) * (residual));

	return sigma;
}

double igarch::log_likelihood(const double* current_return)
{
	double log_igarch(0);
	double residual(0);

	residual = *current_return - *mean;

	log_igarch = -0.5 * log(this-> sigma_t() * this -> sigma_t())
				-0.5 * ((residual * residual) / (this -> sigma_t() * this -> sigma_t()));
}