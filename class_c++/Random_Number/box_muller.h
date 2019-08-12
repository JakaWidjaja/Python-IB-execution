#ifndef BOX_MULLER_H
#define BOX_MULLER_H

class box_muller: public random_number
{
public:
	//Constructor
	box_muller();

	//Destructor
	~box_muller();

	//Generate random number. 
	double random(const double& mu, const double& sigma);
};

	
#endif