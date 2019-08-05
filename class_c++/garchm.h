#ifndef GARCHM_H
#define GARCHM_H

#include "volatility.h"

class garchm : public volatility
{
public:
	//Constructor
	garchm(const double* mean, const double* c,
		   const double* alpha_0, const double* alpha_1,
		   const double* beta, const double* lag_return,
		   const double* lag_vol);

	//Destructor
	~garchm();

	/*
	GARCH-M(1,1)
	squared volatility
	GARCH-M has three different formulas for calculating the return. 
	type-1 is mean + c * (sigma * sigma) + residual
	type-2 is mean + c * sigma + residual
	type-3 is mean + c * ln(sigma * sigma) + residual
	Parameter c is the risk premium parameter. 
	A positive c indicates that the return is positively related to volatility. 
	*/
	virtual double sigma_t(int type = 1);

	//Formula for log likelihood.
	double log_likelihood(const double* current_return);

private:
	const double* mean;
	const double* c;
	const double* alpha_0;
	const double* alpha_1;
	const double* beta;
	const double* lag_return;
	const double* lag_vol;
};

	
#endif