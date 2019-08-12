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
#include "/media/lun/Data2/Trading_Algo/class_c++/Random_Number/random_number.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Random_Number/random_number_generator.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Random_Number/pseudo_uniform_random.h"
#include "/media/lun/Data2/Trading_Algo/class_c++/Random_Number/exponential_random.h"

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

/*
double a123(volatility* bb)
{
	unique_ptr<bb> b123 = make_unique<bb>();

	double kkk = bb123->get_volatility();
	cout << bb123->get_volatility() << endl;
	return kkk;
}
*/
double ccc(double* c1)
{

	return *c1 * *c1;
}

int main()
{

	double a = 8.88;
	double c_stock(100.8);
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


	/*
	unique_ptr<market_implied> imp = make_unique<market_implied>();
	unique_ptr<correlation> correl = make_unique<correlation>();

	cout << "implied: " << imp->get_volatility() << endl;
	cout << "correlation: " << correl-> get_correlation() << endl;
	*/
	unique_ptr<market_implied> mm = make_unique<market_implied>(stock);
	unique_ptr<market_correlation> cc = make_unique<market_correlation>(stock);
	
	//unique_ptr<heston> hest = make_unique<heston>(move(mm));

	//cout << "heston: " << hest->integrand(type, phi) << endl;


	
	unique_ptr<heston> hest_call  = make_unique<heston>(stock, strike, 
					move(mm),
					 move(cc), kappa, theta, lambda, init_var,
					expiry, rate, dividend);
	
	//cout << "heston P1: " << hest_call->p(type1) << endl;
	//cout << "heston P2: " << hest_call->p(type2) << endl;
	//cout << "heston call: " << hest_call->call_price() << endl;
	//cout << "heston put: " << hest_call->put_price() << endl;
	//cout << "integrand: " << hest_call -> integrand(type, phi) << endl;
	


	const unsigned long int seed(88);
	//double beta(8);

	pseudo_uniform_random uniform;
	exponential_random expon(a);

	random_number rando(uniform, expon);

	for(int i = 0; i <10; i++)
	{
		cout << rando.random(seed) << endl;
	}
	//simpsons inter(hest_call->integrand_1(phi), upper_bound, lower_bound, interval);

	//cout<< "integral: " << inter.integrate() << endl;

	/*
	const double& m = 100.5;
	const double& a0 = 0.5;
	const double& a1 = 0.88;
	const double& b = 0.00081;
	const double& lr = 0.5;
	const double& lv = 0.123;
	const double& curr = 0.891;


	double aa = 0.8;

	double cmean = 100.5;
	double calpha_0 = 0.5;
	double calpha_1 = 0.88;
	double cbeta = 0.00081;
	double clag_ret = 0.5;
	double clag_vol = 0.123;
	double ccurrent_return = 0.891;
	double cc = 0.88;
	int type = 3;

	const double* mean = &cmean;
	const double* alpha_0 = &calpha_0;
	const double* alpha_1 = &calpha_1;
	const double* beta = &cbeta;
	const double* lag_ret = &clag_ret;
	const double* lag_vol = &clag_vol;
	const double* current_return = &ccurrent_return;
	const double* c = &cc;

	unique_ptr<igarch> iga = make_unique<igarch>(mean, alpha_0, beta, lag_ret, lag_vol);
	unique_ptr<garch> ga = make_unique<garch> (mean, alpha_0, alpha_1, beta, lag_ret, lag_vol);
	unique_ptr<garchm> gam = make_unique<garchm> (mean, c, alpha_0, alpha_1,  beta, lag_ret, lag_vol);

	cout << "Garch sigma: " << ga -> sigma_t() << endl;
	cout << "Garch Log Likelihood: " << ga -> log_likelihood(current_return) << endl << endl;

	cout << "IGarch sigma: " << iga -> sigma_t() << endl;
	cout << "IGarch Log Likelihood: " << iga -> log_likelihood(current_return) << endl << endl;

	cout << "GarchM sigma: " << gam -> sigma_t(type) << endl;
	cout << "GarchM Log Likelihood: " << gam -> log_likelihood(current_return) << endl << endl;
	
	int bbb = 8;

	cout << "a: " << test(bbb) << endl << endl;

	*/
	return 0;
}