#ifndef IGARCH_H
#define IGARCH_H

#include "volatility.h"

class igarch: public volatility
{
public:
	//constructor
	igarch(const double* mean, const double* alpha_0,
		   const double* beta, const double* lag_return, 
		   const double* lag_vol);

	//destructor
	~igarch();

	//This is the IGARCH model. 
	//IGARCH(1,1)
	virtual double sigma_t();

	//Formula for log likelihood.
	double log_likelihood(const double* current_return);


private:
	const double* mean;
	const double* alpha_0;
	const double* beta;
	const double* lag_return;
	const double* lag_vol;
};


#endif 