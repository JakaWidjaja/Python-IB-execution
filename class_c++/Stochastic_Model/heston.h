#ifndef HESTON_H
#define HESTON_H

#include "stochastic_model.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Volatility/volatility.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Correlation/correlation.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Random_Number/uniform_random_number.h"
#include <memory>

using std::unique_ptr;
using std::make_unique;

class heston: public stochastic_model
{
public:
	
	//Constructor
	//volatility is the volatility of the variance. 
	heston(const double& stock, const double& strike,
		   unique_ptr<volatility> vol, unique_ptr<correlation> correl,
		   const double& kappa, const double& theta,
		   const double& lambda, const double& init_var,
		   const double& expiry, const double& rate,
		   const double& dividend);


	//Destructor
	~heston();

	//Calculate the integrand.	 
	double integrand(const int& type, const double& phi);

	//p1 and p2 is the probability. 
	//p1 is the delta of the europeqn call option. 
	//p2 is the conditional risk neutral probability that the asset 
	//price will be greater than the strike at the maturity
	double p(const int& type);

	//Calculate option call price. 
	double call_price(void);

	//Calculate option put price.
	double put_price(void);

	//Calculation option Call price using Monte-Carlo method. 
	double monte_carlo_call(const int& number_simulation, uniform_random_number& uniform_number);

private:
	const double& stock;
	const double& strike;
	unique_ptr<volatility> vol;
	unique_ptr<correlation> correl;
	const double& kappa;
	const double& theta;
	const double& lambda;
	const double& init_var;
	const double& expiry;
	const double& rate;
	const double& dividend;
};

#endif