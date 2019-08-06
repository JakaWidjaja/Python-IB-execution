#ifndef GARCH_H
#define GARCH_H

#include "volatility.h"

class garch : public volatility
{
public:
	//constructor
	garch(const double& mean, const double& alpha_0, 
		  const double& alpha_1, const double& beta,
		  const double& lag_return, const double& lag_vol);
	
	//destructor
	~garch();

	//Output to calculate the volatility. 
	//This is the garch model.
	//Garch(1,1).
	virtual double get_volatility(void);

	//Formula for log likelihood.
	double log_likelihood(const double& current_return);


private:
	const double& mean;
	const double& alpha_0;
	const double& alpha_1;
	const double& beta;
	const double& lag_return;
	const double& lag_vol;
};

#endif