#include <iostream>
#include <complex>
#include <memory>
#include <math.h>
#include <stdlib.h>
#include "/media/lun/Data2/Trading_Algo/class_c++/Volatility/market_implied.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Correlation/correlation.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Volatility/volatility.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Stochastic_Model/heston.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Correlation/market_correlation.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Random_Number/random_number_generator.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Random_Number/pseudo_uniform_random.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Random_Number/exponential_random.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Random_Number/logistic_random.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Random_Number/box_muller.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Random_Number/cauchy_random.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Random_Number/gamma_random.h"

/*
#include "garch.h"
#include "igarch.h"
#include "garchm.h"
#include "stochastic_model.h"
#include "heston.h"
*/
using std::cout;
using std::endl;
using std::unique_ptr;
using std::make_unique;
using std::complex;
using std::imag;
using std::move;


int main()
{

	double a = 8.88;
	double c_stock(1.8);
	double c_strike(100.8);
	//market_implied* c_vol;
	//correlation* c_correl;
	double c_kappa(0.588);
	double c_theta(0.5);
	double c_lambda(0.085);
	double c_init_var(0.3);
	double c_expiry(0.2);
	double c_rate(0.01);
	double c_dividend(0.0);

	const double& stock = c_stock;
	const double& strike = c_strike;
	const double& kappa = 0.88;
	const double& theta = c_theta;
	const double& lambda = c_lambda;
	const double& init_var = c_init_var;
	const double& expiry = c_expiry;
	const double& rate = c_rate;
	const double& dividend = c_dividend;
	int type1 = 1;
	int type2 = 2;
	double phi = 20.0;

	unique_ptr<market_implied> mm = make_unique<market_implied>(stock);
	unique_ptr<market_correlation> cc = make_unique<market_correlation>(stock);
	
	//unique_ptr<heston> hest = make_unique<heston>(move(mm));

	//cout << "heston: " << hest->integrand(type, phi) << endl;


	
	unique_ptr<heston> hest_call  = make_unique<heston>(stock, strike, 
					move(mm),
					 move(cc), kappa, theta, lambda, init_var,
					expiry, rate, dividend);
	

	const unsigned long int seed(88);
	double mu (0.88);
	double sigma(1.0);

	pseudo_uniform_random uniform(seed);
	gamma_random expon(uniform, mu, sigma);


	for(int i = 0; i <20; i++)
	{
		cout << expon.generate_number() << endl;
	}


	int arr[] = {1879,2888};

	cout << "first: " << arr[0] << endl;
	cout << "second: " << arr[1] << endl;

	return 0;
}