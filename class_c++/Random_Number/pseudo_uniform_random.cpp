#include "pseudo_uniform_random.h"

//Constructor
pseudo_uniform_random::pseudo_uniform_random():v(4101842887655102017LL)
{}

//Destructor
pseudo_uniform_random::~pseudo_uniform_random()
{}

double pseudo_uniform_random::generate_number(const unsigned long int& seed)
{

	v ^= seed;
	v ^= v >> 21;
	v ^= v << 35;
	v ^= v >> 4;
	v *= 2685821657736338717LL;

	return  5.4210108624275221E-20 * v;
}