#include "heston.h"
#include <string>
#include <complex>
#include <math.h>
#include <memory>
#include "volatility.h"
#include "correlation.h"
#include "numerical_integration.h"
#include "simpsons.h"

using std::string;
using std::complex;
using std::real;
using std::unique_ptr;
using std::make_unique; 
using std::move;

//Constructor
heston::heston(const double& c_stock, const double& c_strike,
		   	   unique_ptr<volatility> c_vol, unique_ptr<correlation> c_correl,
		   	   const double& c_kappa, const double& c_theta,
		   	   const double& c_lambda, const double& c_init_var,
		   	   const double& c_expiry, const double& c_rate,
		   	   const double& c_dividend):
	stock(c_stock), strike(c_strike), kappa(c_kappa), theta(c_theta),
	lambda(c_lambda), init_var(c_init_var), expiry(c_expiry), rate(c_rate),
	dividend(c_dividend)
{
	vol = move(c_vol);
	correl = move(c_correl);
}

//Destructor
heston::~heston()
{}


//Integrand function. 
double heston::integrand(const int& type, const double& phi)
{
	if (phi == 0.0)
	{
		return 0.0;
	}
	else
	{
	//Initialising parameters.
	double param_u(0.0);
	double param_b(0.0);
	double param_a(0.0);
	complex<double> param_g;
	complex<double> param_D;
	complex<double> param_f;
	complex<double> param_c;
	complex<double> one_real(1.0, 0.0);
	complex<double> minus_one_real(-1.0, 0.0);
	complex<double> two_real(2.0, 0.0);
	complex<double> output;

	if (type == 1)
	{
		param_u = 0.5;
		param_b = kappa + lambda - correl->get_correlation() * vol->get_volatility();
	}
	else if (type == 2)
	{
		param_u = -0.5;
		param_b = kappa + lambda;
	}


	//Calculate parameter a.
	param_a = (kappa) * (theta);

	//Calculate parameter small d.
	complex<double> param_d(param_b * param_b - (correl->get_correlation()) * (vol->get_volatility()) * 
							(vol->get_volatility()) * phi * phi + //real part
					  		(vol->get_volatility()) * (vol->get_volatility()) * phi * phi , 
					  		2 * vol->get_volatility() * phi * (param_b * (correl->get_correlation()) + //Imaginary part
					  		(vol->get_volatility()) * param_u)); //Imaginary part

	param_d = sqrt(param_d);
	
	//Calculate parameter g.
	complex<double> numerator(param_b, 
							  correl->get_correlation() * vol->get_volatility() * phi * -1);

	complex<double> denominator(param_b, 
								correl -> get_correlation() * vol->get_volatility() * phi * -1);

	param_g = (numerator + param_d) / (denominator - param_d);

	//Calculate parameter big D.
	complex<double> numerator_1(param_b, -1 * (correl->get_correlation()) 
								* (vol->get_volatility()) * phi);
	complex<double> denominator_1((vol->get_volatility()) * (vol->get_volatility()), 0.0);

	complex<double> temp1 = param_d * (expiry) * minus_one_real;
	complex<double> numerator_2 = one_real - exp(temp1);
	complex<double> denominator_2 = one_real - param_g * exp(temp1);

	param_D = (numerator_1 - param_d) / denominator_1 * (numerator_2 / denominator_2);

	//Calculate parameter c.
	complex<double> temp2(0.0, (expiry) * phi * (rate));
	complex<double> temp3((kappa) * (theta) / (vol->get_volatility() * vol->get_volatility()), 0.0);
	complex<double> temp4(param_b, 0.0);
	complex<double> temp5(0.0, correl->get_correlation() * vol->get_volatility() * phi);

	param_c = temp2 + temp3 * ((temp4 - temp5- param_d) * (expiry) - two_real * 
			  log((one_real - param_g * exp(temp1)) / (one_real - param_g)));

	//Calculate parameter f.
	complex<double> temp6(0.0, phi * log(stock));

	param_f = exp(param_c) + exp(param_D * (init_var)) + exp(temp6);

	//Calculate the output. 
	complex<double> temp7(0.0, phi * log(strike));
	complex<double> temp8(0.0, phi);

	output = exp(temp7) * param_f / temp8;
	
	return real(output);
	}
}

double heston::p(const int& type)
{
	//Create the mathematical constant pi.
	const double pi = 3.14159265359;

	double sum1(0.0);
	double sum2(0.0);
	double area(0.0);
	double result(0.0);
	double dx(0.0);
	double u(0.0);

	//Set the upper bound, lower bound and interval. 
	double upper_bound(10000.0);
	double lower_bound(0.0); 
	int interval(1000);

	//Integrate the function using simpson's rule. 
	dx = (upper_bound - lower_bound) / interval;
	u = lower_bound + dx;

	for (int i = 1; i < interval; i++)
	{
		if(i % 2 != 0)
            sum1 += (integrand)(type, u);
        else
            sum2 += (integrand)(type, u);
        
        u += dx;
	}

	area = (integrand)(type, lower_bound) + (integrand)(type, upper_bound) + 4.0 * sum1 + 2.0 * sum2;
    area *= dx / double(3.0); 

	return 0.5 + (1/pi) * area;
}


//Calculate option CALL price using heston volatility model. 
double heston::call_price(void)
{
	double option_price;
	int type1(1);
	int type2(2);

	option_price = stock * this->p(type1) - strike * exp((dividend - rate) * expiry) * this->p(type2);

	return option_price;
	
}

//Calculate option PUT price using heston volatility model. 
//Using the call-put parity
double heston::put_price(void)
{
	double option_price;

	option_price = this->call_price() - stock + strike * exp((dividend - rate) * expiry);

	return option_price;
}

//Calculate option CALL price using monte carlo method. 
double heston::monte_carlo_call(const int& number_simulation)
{

}