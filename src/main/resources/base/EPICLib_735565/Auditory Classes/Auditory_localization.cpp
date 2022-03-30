//
//  Auditory_localization.cpp
//  EPIC
//
//  Created by David Kieras on 9/9/13.
//  Copyright (c) 2013 David Kieras. All rights reserved.
//

/*
 This uses an localization function worked out by Greg Wakefield circa June 30, 2013
 using a combination of results from Oldfield and Middlebrooks.
 It flips a coin to decide whether there is a front-back reversal.
*/

#include "Auditory_localization.h"
#include "../Standard_Symbols.h"
#include "../Utility Classes/Numeric_utilities.h"
#include "../Utility Classes/Random_utilities.h"
#include "../Framework classes/Output_tee_globals.h"

// add error variability to location of a an auditory object
// returned value is erroneous location

static double modify_angle(double);
static double compute_bias(double);
static double compute_reversal(double);
static double compute_sd(double);

// disabled 6/26/14 for NSMRL work

GU::Point apply_auditory_location_error(GU::Point original_location)
{
    return original_location;
/*
    // location error in azimuth only
    double x = original_location.x;
	if (x <= 180.) { // for right side
		x = modify_angle(x);
		}
	else {  // for left side
		x = 360. - x; // transform to same scale as right side		if(debug_messages)
		x = modify_angle(x);
        x = 360. - x; // transform back
		}

	return GU::Point(x, original_location.y);
*/
}

// modify the supplied angle with noise, biased, and flipped in some order
double modify_angle(double original_angle)
{
	double sd = compute_sd(original_angle);
	double bias = compute_bias(original_angle);
	double biased_angle = original_angle + bias;
	double x = normal_random_variable(biased_angle, sd);
	x = compute_reversal(x);
	return x;
}


// return the sd for the guassian error sampling
double compute_sd (double x)
{
// based on Middlebrooks
// =-0.00000007337*A2^4+0.00001787*A2^3-0.001513*A2^2+0.1231*A2+2.29
	const double a4 = -0.0000000733;
	const double a3 = +0.00001787;
	const double a2 = -0.001513;
	const double a1 = +0.1231;
	const double a0 = +2.29;
	
	double sd = a4 * (x * x * x * x) + a3 * (x * x *x) + a2 * (x * x) + a1 * (x) + a0;
	return sd;
}

// return the biased_angle computed as a function of the angle
double compute_bias(double x)
{
// based on combined Oldfield & Middlebrooks data
// =0.0000002801*A17^4-0.00007509*A17^3+0.004356*A17^2+0.006655*A17+0.1454
	const double a4 = 0.0000002801;
	const double a3 = -0.00007509;
	const double a2 = +0.004356;
	const double a1 = +0.006655;
	const double a0 = +0.1454;
	
	double biased = a4 * (x * x * x * x) + a3 * (x * x *x) + a2 * (x * x) + a1 * (x) + a0;
	return biased;
}

// Flip a coin that follows a bell curve probability roughly centered on 90 degrees
// The probability of the coin follows a gaussian curve, but this is not a gaussian distribution.
// Return either the original value or the flipped value.
double compute_reversal(double original_angle)
{
	const double m = 90.;
	const double s = 57.9;
	const double a = 62.54;
	const double b = 0.01318;
	const double c = 0.278;
	
	// compute value to compare to uniform random variable
	double az = (original_angle - m) / s;
	double z = (az - b) / c;
	double p = a * exp(-(z*z));
	
	double x = unit_uniform_random_variable();
	if(x <= p)
		return 180. - original_angle;// reverse
	else
		return original_angle;
}
