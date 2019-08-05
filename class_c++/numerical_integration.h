#ifndef NUMERICAL_INTEGRATION_H
#define NUMERICAL_INTEGRATION_H

template<class T>
class numerical_integration
{	
public:
	//Constructor
	numerical_integration<T>();

	//Destructor
	~numerical_integration();

	virtual double integrate(T* func) = 0;

};

#endif