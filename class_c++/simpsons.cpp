#include "simpsons.h"

//constructor
template <class T>
simpsons<T>::simpsons(const double& c_lower_bound, const double& c_upper_bound,
					 const int& c_interval)
{
	//func = c_func;
	lower_bound = c_lower_bound;
	upper_bound = c_upper_bound;
	interval = c_interval;
}

//Destructor
template <class T>
simpsons<T>::~simpsons()
{}

template <class T>
double simpsons<T>::integrate(T* func)
{
	//Create the mathematical constant pi. 
	const double pi = 3.14159265359;

	double sum1(0.0);
    double sum2(0.0);
    double area(0.0);
    double result(0.0);
    double dx(0.0);
    double u(0.0);
    
    //Integrate the function using simpson's rule. 
    dx = (upper_bound - lower_bound) / interval;
    u = lower_bound + dx;

    for (int i = 1; i < interval; i++)
    {
        if(i % 2 != 0)
            sum1 += (*func)(u);
        else
            sum2 += (*func)(u);
        
        u += dx;
    }
    
    area = (*func)(lower_bound) + (*func)(upper_bound) + 4.0 * sum1 + 2.0 * sum2;
    area *= dx / double(3.0); 
    
    return area;
}
