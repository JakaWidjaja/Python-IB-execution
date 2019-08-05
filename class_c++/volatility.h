#ifndef VOLATILITY_H
#define VOLATILITY_H

//Abstract base Class.
class volatility
{
public:
	//Constructor.
	volatility();

	//Destructor.
	virtual ~volatility(void);


	virtual double get_volatility() = 0;

};

#endif