#include "gamma_random.h"
#include <math.h>
#include "box_muller.h"

//Constructor
gamma_random::gamma_random(uniform_random_number& c_uniform_number, 
							double& c_alpha, const double& c_beta):
							uniform_number(c_uniform_number), alpha(c_alpha), beta(c_beta)
{
	if (alpha <= 0.0)
	{
		throw("Bad Alpha");
	}

	if (alpha < 1.0)
	{
		alpha += 1.0;
	}

}

//Destructor
gamma_random::~gamma_random()
{}

double gamma_random::generate_number()
{
	double a1;
	double a2;
	double u;
	double v;
	double x;

	box_muller normal_random(uniform_number, 0.0, 1.0);

	a1 = alpha - 1.0/3.0;
	a2 = 1.0 / sqrt(9.0 * a1);

	do 
	{
		do
		{
			x = normal_random.generate_number();
			v = 1.0 + a2 * x;
		}while(v <= 0.0);

		v = v * v * v;
		u = uniform_number.generate_number();

	}while ((u > 1.0 - 0.331 * (x * x) * (x * x)) && 
			(log(u) > 0.5 * x * x + a1 * (1.0 - v + log(v)))); //Rarely evaluated. 

	if (alpha < 1.0)
	{
		return a1 * v / beta;
	}
	else
	{
		do
		{
			u = uniform_number.generate_number();
		}while (u == 0.0);

		return (pow(u, 1.0 / alpha) * a1 * v /beta);
	}
}