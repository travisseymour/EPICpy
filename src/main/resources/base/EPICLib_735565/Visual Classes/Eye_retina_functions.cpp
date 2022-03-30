#include "Eye_retina_functions.h"
#include <cmath>
#include <sstream>

#include "Visual_physical_store.h"
#include "../Epic_standard_symbols.h"
#include "../Utility Classes/Random_utilities.h"
#include "../Utility Classes/Assert_throw.h"


using std::pow;
using std::string;
using std::ostringstream;
using std::istringstream;


Availability * Availability::create(const Visual_physical_store& physical_store, const Parameter_specification& param_spec)
{
	istringstream iss(param_spec.specification);
	// first term is property name
	string property_name;
	iss >> property_name;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read property name in parameter specification", param_spec);
	Symbol prop_name(property_name);
	// second term is availability function type, followed by terms depending on type
	string func_type;
	iss >> func_type;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read availability function type in parameter specification", param_spec);
	// let each availability type parse the rest of the input
	if(func_type == "Flat")
		return Flat_availability::create(physical_store, prop_name, param_spec, iss);
	if(func_type == "Selector")
		return Selector_availability::create(physical_store, prop_name, param_spec, iss);
	if(func_type == "Custom")
		return Custom_availability::create(physical_store, prop_name, param_spec, iss);
	if(func_type == "Custom2")
		return Custom_availability2::create(physical_store, prop_name, param_spec, iss);
	if(func_type == "Zone")
		return Zone_availability::create(physical_store, prop_name, param_spec, iss);
	if(func_type == "Linear")
		return Linear_availability::create(physical_store, prop_name, param_spec, iss);
	if(func_type == "Fixed_quadratic")
		return Fixed_quadratic_availability::create(physical_store, prop_name, param_spec, iss);
	if(func_type == "Quadratic")
		return Quadratic_availability::create(physical_store, prop_name, param_spec, iss);
	if(func_type == "Fixed_exponential")
		return Fixed_exponential_availability::create(physical_store, prop_name, param_spec, iss);
	if(func_type == "Exponential")
		return Exponential_availability::create(physical_store, prop_name, param_spec, iss);
		
	Parameter::throw_parameter_error("Unrecognized availability function type in parameter specification", param_spec);
	return 0;
}

/* 
Zone availability means the property is all-or-none available within a certain
radius; if it is within the "standard" fovea, it is always available, regardless 
of the eccentricity fluctuation. Otherwise, it is available if it is within
a property-specific "parafoveal" distance as modified by the fluctuation, 
and has a property-specific delay.
*/

bool Zone_availability::available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation)
{
	double eccentricity = physobj_ptr->get_eccentricity();
	return ( (eccentricity  * eccentricity_fluctuation) < zone_radius);
}

long Zone_availability::delay(Smart_Pointer<Visual_store_object>, double time_fluctuation)
{
	return long(transduction_delay * time_fluctuation);
}

string Zone_availability::get_description() const
{
	ostringstream oss;
	oss << get_property_name() << ": Zone available inside " << zone_radius 
		<< " degrees eccentricity after " << transduction_delay << " ms.";
	return oss.str();
}

Availability * Zone_availability::create(const Visual_physical_store& physical_store, const Symbol& prop_name, 
		const Parameter_specification& param_spec, istringstream& iss)
{
	long delay;
	iss >> delay;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read availability delay in parameter specification", param_spec);
	double zone_radius;
	iss >> zone_radius;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read radius in parameter specification", param_spec);
	if(zone_radius < standard_fovea_radius)
		Parameter::throw_parameter_error("Zone radius must be >= than standard fovea radius", param_spec);
	if(zone_radius > standard_peripheral_radius)
		Parameter::throw_parameter_error("Zone radius must be <= than standard peripheral radius", param_spec);
	return new Zone_availability(physical_store, prop_name, delay, zone_radius);
}


/* "Standard" default availabilities based on the LISP EPIC defaults
These are zone availabilities that use the "standard" values for fovea, parafovea, and periphery.
*/

Relation_std_zone_availability::Relation_std_zone_availability(const Visual_physical_store& physical_store_, const Symbol& property_name_) :
	Periphery_std_zone_availability(physical_store_, property_name_)
{}

Color_std_zone_availability::Color_std_zone_availability(const Visual_physical_store& physical_store_) :
	Parafovea_std_zone_availability(physical_store_, Color_c)
{}

Shape_std_zone_availability::Shape_std_zone_availability(const Visual_physical_store& physical_store_) :
	Parafovea_std_zone_availability(physical_store_, Shape_c, standard_long_delay)
{}

Text_std_zone_availability::Text_std_zone_availability(const Visual_physical_store& physical_store_) :
	Fovea_std_zone_availability(physical_store_, Text_c, standard_long_delay)
{}

// End of "standard" zone availabilities

/* Flat availability means the property is all-or-none available with a certain
probability regardless of where it is outside the fovea.
if it is within the "standard" fovea, it is always available.
*/
bool Flat_availability::available(Smart_Pointer<Visual_store_object> physobj_ptr, double )
{
	double eccentricity = physobj_ptr->get_eccentricity();
	return (
		eccentricity <= standard_fovea_radius
		|| 
		probability >= unit_uniform_random_variable()
		);
}

long Flat_availability::delay(Smart_Pointer<Visual_store_object>, double time_fluctuation)
{
	return long(transduction_delay * time_fluctuation);
}

string Flat_availability::get_description() const
{
	ostringstream oss;
	oss << get_property_name() << ": Flat available with probability " << probability 
		<< " after " << transduction_delay << " ms.";
	return oss.str();
}

Availability * Flat_availability::create(const Visual_physical_store& physical_store, const Symbol& prop_name, 
		const Parameter_specification& param_spec, istringstream& iss)
{
	long delay;
	iss >> delay;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read availability delay in parameter specification", param_spec);
	double prob;
	iss >> prob;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read probability in parameter specification", param_spec);
	return new Flat_availability(physical_store, prop_name, delay, prob);
}


/* Selector availability means the property is all-or-none available with a certain
probability if it has a certain value, and not otherwise, except 
if it is within the "standard" fovea, it is always available.
*/
bool Selector_availability::available(Smart_Pointer<Visual_store_object> physobj_ptr, double )
{
	double eccentricity = physobj_ptr->get_eccentricity();
	if(eccentricity <= standard_fovea_radius)
		return true;
	if(physobj_ptr->get_property_value(get_property_name()) == selected_value)
		return (probability >= unit_uniform_random_variable());
	else
		return false;
}

long Selector_availability::delay(Smart_Pointer<Visual_store_object>, double time_fluctuation)
{
	return long(transduction_delay * time_fluctuation);
}

string Selector_availability::get_description() const
{
	ostringstream oss;
	oss << get_property_name() << ": Selected value " << selected_value << " available with probability " << probability 
		<< " after " << transduction_delay << " ms.";
	return oss.str();
}

Availability * Selector_availability::create(const Visual_physical_store& physical_store, const Symbol& prop_name, 
		const Parameter_specification& param_spec, istringstream& iss)
{
	long delay;
	iss >> delay;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read availability delay in parameter specification", param_spec);
	string value_str;
	iss >> value_str;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read selected value in parameter specification", param_spec);
	double prob;
	iss >> prob;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read probability in parameter specification", param_spec);
	return new Selector_availability(physical_store, prop_name, delay, Symbol(value_str), prob);
}

/* Custom availability provides an arbitrary function for determining availability.
This is intended as an aid to data fitting.
*/
bool Custom_availability::available(Smart_Pointer<Visual_store_object> physobj_ptr, double )
{
	double eccentricity = physobj_ptr->get_eccentricity();
	
	if(eccentricity <= standard_fovea_radius)
		return true;
	
	if(eccentricity < 8.)
		return (0.70 >= unit_uniform_random_variable());
	else
		return (0.30 >= unit_uniform_random_variable());
}

long Custom_availability::delay(Smart_Pointer<Visual_store_object>, double time_fluctuation)
{
	return long(transduction_delay * time_fluctuation);
}

string Custom_availability::get_description() const
{
	ostringstream oss;
	oss << get_property_name() << ": Custom availability if ecc < 8, .70, else .30 after " << transduction_delay << " ms.";
	return oss.str();
}

Availability * Custom_availability::create(const Visual_physical_store& physical_store, const Symbol& prop_name, 
		const Parameter_specification& param_spec, istringstream& iss)
{
	long delay;
	iss >> delay;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read availability delay in parameter specification", param_spec);
/*	string value_str;
	iss >> value_str;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read selected value in parameter specification", param_spec);
	double prob;
	iss >> prob;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read probability in parameter specification", param_spec);
*/
	return new Custom_availability(physical_store, prop_name, delay);
}

/* Custom availability provides an arbitrary function for determining availability.
This is intended as an aid to data fitting.
*/
bool Custom_availability2::available(Smart_Pointer<Visual_store_object> physobj_ptr, double )
{
	double eccentricity = physobj_ptr->get_eccentricity();
	
	if(eccentricity <= standard_fovea_radius)
		return true;
	
	if(eccentricity < 8.)
		return (0.70 >= unit_uniform_random_variable());
	else
		return (0.20 >= unit_uniform_random_variable());
}

long Custom_availability2::delay(Smart_Pointer<Visual_store_object>, double time_fluctuation)
{
	return long(transduction_delay * time_fluctuation);
}

string Custom_availability2::get_description() const
{
	ostringstream oss;
	oss << get_property_name() << ": Custom2 availability if ecc < 8, .70, else .2 after " << transduction_delay << " ms.";
	return oss.str();                                 
	
}

Availability * Custom_availability2::create(const Visual_physical_store& physical_store, const Symbol& prop_name, 
		const Parameter_specification& param_spec, istringstream& iss)
{
	long delay;
	iss >> delay;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read availability delay in parameter specification", param_spec);
/*	string value_str;
	iss >> value_str;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read selected value in parameter specification", param_spec);
	double prob;
	iss >> prob;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read probability in parameter specification", param_spec);
*/
	return new Custom_availability2(physical_store, prop_name, delay);
}



/*
Linear availability requires that an object size be larger than a value specified
as a linear function extending from the standard fovea radius out to the periphery.
The function specifies the minimum size for an object within the fovea,
and the slope for the function. All units are in degrees VA.
The delay is a flat value for the property.
*/
bool Linear_availability::available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation)
{
	double eccentricity = physobj_ptr->get_eccentricity() * eccentricity_fluctuation;
	// use the average of horizontal and vertical size
	double obj_size = (physobj_ptr->get_size().h + physobj_ptr->get_size().v) / 2.0;
	double x = eccentricity - standard_fovea_radius;
	double threshold_size = (x < 0.) ? min_size : x * slope + min_size;
	return (obj_size > threshold_size);
}		

long Linear_availability::delay(Smart_Pointer<Visual_store_object>, double time_fluctuation)
{
	return long(transduction_delay * time_fluctuation);
}

string Linear_availability::get_description() const
{
	ostringstream oss;
	oss << get_property_name() << ": Linearly available with minimum size " << min_size 
		<< " degrees in fovea, and slope " << slope << " per degree eccentricity outside fovea after " << transduction_delay << " ms.";
	return oss.str();
}

Availability * Linear_availability::create(const Visual_physical_store& physical_store, const Symbol& prop_name, 
		const Parameter_specification& param_spec, istringstream& iss)
{
	long delay;
	iss >> delay;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read availability delay in parameter specification", param_spec);
	double min_size;
	iss >> min_size;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read min_size in parameter specification", param_spec);
	double slope;
	iss >> slope;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read slope in parameter specification", param_spec);

	return new Linear_availability(physical_store, prop_name, delay, min_size, slope);
}


/*
Quadratic availability requires that an object size be larger than a value specified
as a 2nd-order polynomial function extending from eccentricity = 0 out to the periphery.
The function is in the form: y = intercept + x_coeff * x + x2_coeff * x^2
The function specifies the minimum size for an object.
All units are in degrees VA.
The delay is a flat value for the property.
*/
bool Fixed_quadratic_availability::available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation)
{
	double eccentricity = physobj_ptr->get_eccentricity() * eccentricity_fluctuation;
	// use the average of horizontal and vertical size
	double obj_size = (physobj_ptr->get_size().h + physobj_ptr->get_size().v) / 2.0;
	double threshold_size = intercept + x_coeff * eccentricity + x2_coeff * eccentricity * eccentricity;
	return (obj_size > threshold_size);
}		

long Fixed_quadratic_availability::delay(Smart_Pointer<Visual_store_object>, double time_fluctuation)
{
	return long(transduction_delay * time_fluctuation);
}

string Fixed_quadratic_availability::get_description() const
{
	ostringstream oss;
	oss << get_property_name() << ": Fixed quadratically available with intercept " << intercept 
		<< ", linear " << x_coeff << ", and quadratic " << x2_coeff 
		<< " components per degree eccentricity after " << transduction_delay << " ms.";
	return oss.str();
}

Availability * Fixed_quadratic_availability::create(const Visual_physical_store& physical_store, const Symbol& prop_name, 
		const Parameter_specification& param_spec, istringstream& iss)
{
	long delay;
	iss >> delay;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read availability delay in parameter specification", param_spec);
	double intercept;
	iss >> intercept;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read intercept in parameter specification", param_spec);
	double x_coeff;
	iss >> x_coeff;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read x_coeff in parameter specification", param_spec);
	double x2_coeff;
	iss >> x2_coeff;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read x2_coeff in parameter specification", param_spec);

	return new Fixed_quadratic_availability(physical_store, prop_name, delay, intercept, x_coeff, x2_coeff);
}

/*
Quadratic availability requires that an object size plus a Normal fluctuation be larger than a value specified
as a 2nd-order polynomial function extending from eccentricity = 0 out to the periphery.
The object is available if (object_size + fluctuation) > intercept + x_coeff * x + x2_coeff * x^2
where fluctuation is Normal(0., coefvar * object_size)
If ecc < zone, then always available. Normally, zone should be either 0 - meaning an acuity failure can happen
for a fixated object, or something like 1.0 which means the property is always available for a fixated
or foveated object. 
All units are in degrees VA.
The delay is a constant value for the property.
*/
bool Quadratic_availability::available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation)
{
	double eccentricity = physobj_ptr->get_eccentricity() * eccentricity_fluctuation;
	// use the average of horizontal and vertical size
	double obj_size = (physobj_ptr->get_size().h + physobj_ptr->get_size().v) / 2.0;
// Superseded 2/28/08 - DK
//	if(eccentricity < 1.0 && obj_size > 0.1)
//		return true;
	if(eccentricity < zone)
		return true;
	double threshold_size = intercept + x_coeff * eccentricity + x2_coeff * eccentricity * eccentricity;
	double fluctuation = normal_random_variable(0., coefvar * obj_size);
	return (obj_size + fluctuation > threshold_size);
}		

long Quadratic_availability::delay(Smart_Pointer<Visual_store_object>, double time_fluctuation)
{
	return long(transduction_delay * time_fluctuation);
}

string Quadratic_availability::get_description() const
{
	ostringstream oss;
	oss << get_property_name() << ": Quadratically available outside eccentricity of " << zone << " with coefficient of variation "  << coefvar << ", intercept " << intercept
		<< ", linear " << x_coeff << ", and quadratic " << x2_coeff 
		<< " components per degree eccentricity and " << transduction_delay << " ms delay.";
	return oss.str();
}

Availability * Quadratic_availability::create(const Visual_physical_store& physical_store, const Symbol& prop_name, 
		const Parameter_specification& param_spec, istringstream& iss)
{
	long delay;
	iss >> delay;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read availability delay in parameter specification", param_spec);
	double zone;
	iss >> zone;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read zone in parameter specification", param_spec);
	double coefvar;
	iss >> coefvar;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read coefficient of variation in parameter specification", param_spec);
	double intercept;
	iss >> intercept;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read intercept in parameter specification", param_spec);
	double x_coeff;
	iss >> x_coeff;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read x_coeff in parameter specification", param_spec);
	double x2_coeff;
	iss >> x2_coeff;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read x2_coeff in parameter specification", param_spec);

	return new Quadratic_availability(physical_store, prop_name, delay, zone, coefvar, intercept, x_coeff, x2_coeff);
}

/*
Exponential availability requires that an object size be larger than a value specified
as exponential function extending from eccentricity = 0 out to the periphery.
The function is in the form: y = coef *  base^(expon * x)
The function specifies the minimum size for an object.
All units are in degrees VA.
The delay is a flat value for the property.
*/
bool Fixed_exponential_availability::available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation)
{
	double eccentricity = physobj_ptr->get_eccentricity() * eccentricity_fluctuation;
	// use the average of horizontal and vertical size
	double obj_size = (physobj_ptr->get_size().h + physobj_ptr->get_size().v) / 2.0;
	double threshold_size = coeff * exp(expon * eccentricity);
	return (obj_size > threshold_size);
}		

long Fixed_exponential_availability::delay(Smart_Pointer<Visual_store_object>, double time_fluctuation)
{
	return long(transduction_delay * time_fluctuation);
}

string Fixed_exponential_availability::get_description() const
{
	ostringstream oss;
	oss << get_property_name() << ": Fixed exponentially available with coefficient " << coeff 
		<< ", and exponent " << expon 
		<< " components per degree eccentricity after " << transduction_delay << " ms.";
	return oss.str();
}

Availability * Fixed_exponential_availability::create(const Visual_physical_store& physical_store, const Symbol& prop_name, 
		const Parameter_specification& param_spec, istringstream& iss)
{
	long delay;
	iss >> delay;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read availability delay in parameter specification", param_spec);
	double coeff;
	iss >> coeff;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read coefficient in parameter specification", param_spec);
	double expon;
	iss >> expon;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read exponent in parameter specification", param_spec);

	return new Fixed_exponential_availability(physical_store, prop_name, delay, coeff, expon);
}

/*
Fluctuation Exponential availability requires that an object size plus a Normal fluctuation 
be larger than a value specified as exponential function extending from eccentricity = 0 out to the periphery.
The function is in the form: y = coef *  exp(expon * x).
The object is available if (object_size + fluctuation) > coef *  exp(expon * x)
where fluctuation is Normal(object_size, coefvar * object_size)
For foveal objects (ecc < 1) and size > .1 DVA, always available.
All units are in degrees VA.
The delay is a flat value for the property.
*/

bool Exponential_availability::available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation)
{
	double eccentricity = physobj_ptr->get_eccentricity() * eccentricity_fluctuation;
	// use the average of horizontal and vertical size
	double obj_size = (physobj_ptr->get_size().h + physobj_ptr->get_size().v) / 2.0;
	if(eccentricity < 1.0 && obj_size > 0.1)
		return true;
	double threshold_size = coeff * exp(expon * eccentricity);
	double fluctuation = normal_random_variable(0., coefvar * obj_size);
	return (obj_size + fluctuation > threshold_size);
}		

long Exponential_availability::delay(Smart_Pointer<Visual_store_object>, double time_fluctuation)
{
	return long(transduction_delay * time_fluctuation);
}

string Exponential_availability::get_description() const
{
	ostringstream oss;
	oss << get_property_name() << ": Exponential available with coefficient of variation " << coefvar << ", coefficient " << coeff 
		<< ", and exponent " << expon 
		<< " after " << transduction_delay << " ms.";
	return oss.str();
}

Availability * Exponential_availability::create(const Visual_physical_store& physical_store, const Symbol& prop_name, 
		const Parameter_specification& param_spec, istringstream& iss)
{
	long delay;
	iss >> delay;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read availability delay in parameter specification", param_spec);
	double coefvar;
	iss >> coefvar;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read coefficient of variation in parameter specification", param_spec);
	double coeff;
	iss >> coeff;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read coefficient in parameter specification", param_spec);
	double expon;
	iss >> expon;
	if(!iss)
		Parameter::throw_parameter_error("Unable to read exponent in parameter specification", param_spec);

	return new Exponential_availability(physical_store, prop_name, delay, coefvar, coeff, expon);
}




/**** SPECIFIC PROPERTY AVAILABILITY FUNCTIONS ****/

// These are specific availability function that uses the general functions

// The design is flawed, in that we can't change the general function without
// forcing recompiles of many visual-related components - this is due to the
// use of inheritance for implementation!

/* Color availability */
	
//Color_quad_availability uses a Fixed_quadratic_availability model, but special-cases "Red" if 
//it is not available. All units are in degrees VA.
//The delay is a flat value for the property.

Color_quad_availability::Color_quad_availability(const Visual_physical_store& physical_store_, long delay_) :
	Fixed_quadratic_availability(physical_store_, Color_c, delay_, .5, 0.02, 0.0001), red_min_size(1.5)
{
}
bool Color_quad_availability::available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation)
{
	// the color is available generally, return true
	if(Fixed_quadratic_availability::available(physobj_ptr, eccentricity_fluctuation))
		return true;
	// see if the Color is Red - it gets special treatment
	if(physobj_ptr->get_property_value(get_property_name()) == Red_c) {
		// use the average of horizontal and vertical size
		double obj_size = (physobj_ptr->get_size().h + physobj_ptr->get_size().v) / 2.0;
		return (obj_size >= red_min_size);
		}
	return false;
}		


	// 5/02/03 Use exponential availability based on 80% threshold X0213 analysis 4/29/03
	// Fixed_exponential_availability(physical_store_, "Color", delay_, 0.095, 10.0, 0.024)
	// 5/22/03 Use exponential availability based on 90% threshold X0213 analysis 4/29/03
	// Fixed_exponential_availability(physical_store_, "Color", delay_, 0.147, 10.0, 0.025)
	// 5/22/03 Use exponential availability based on ridiculous values
	// below makes colors visible over about two-thirds the VisSearch display, about 6 rows/columns away
	// if eye is centered, almost all colors are visible
	// Fixed_exponential_availability(physical_store_, "Color", delay_, 0.15, 10.0, 0.05)
	// below makes colors visible over about a third of the VisSearch display, about 4 rows/columns away
	// Fixed_exponential_availability(physical_store_, "Color", delay_, 0.15, 10.0, 0.08)
	// below makes colors visible over about a quarter of the VisSearch display, about 2 rows or columns away
Color_exp_availability::Color_exp_availability(const Visual_physical_store& physical_store_, long delay_) :
	Fixed_exponential_availability(physical_store_, Color_c, delay_, 0.15, 0.10)
{
}


/* Shape availability */
//  Shape_zone_availability

//A simple Fixed_quadratic_availability model. 
//The delay is a flat value for the property.
//These values are just those from Anstis's single-letter study.
Shape_quad_availability::Shape_quad_availability(const Visual_physical_store& physical_store_, long delay_) :
	Fixed_quadratic_availability(physical_store_, Shape_c, delay_, 0.104, 0.024, 0.001)
{
}

// 5/02/03 Use exponential availability based on 80% threshold X0216 analysis 4/29/03
Shape_exp_availability::Shape_exp_availability(const Visual_physical_store& physical_store_, long delay_) :
	Fixed_exponential_availability(physical_store_, Shape_c, delay_, 0.304, 0.013)
{
}

/* Text availability */

// Quadratic, but the object size has to be estimated and reduced for flanker effects
// from neighboring letters, we can't just use Fixed_quadratic_availability.
// This is a crude hack - do not assume these are anywhere near right.
Text_availability::Text_availability(const Visual_physical_store& physical_store_, long delay_) :
	// double the values from the data to get simple assumption that letters are half the height of the object
	Availability(physical_store_, Text_c), transduction_delay(delay_), 
	intercept(0.104),x_coeff(0.024), x2_coeff(0.001)
{
}

bool Text_availability::available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation)
{
	double eccentricity = physobj_ptr->get_eccentricity() * eccentricity_fluctuation;
	// threshold - if foveated it can be seen
	if(eccentricity <= standard_fovea_radius)
		return true;
	// kludge - assume the text height is half the object height
	double height = physobj_ptr->get_size().v / 2.0;
	// get the text itself
	Symbol text = physobj_ptr->get_property_value(get_property_name());
	// crude hack: flanker effects divide height by the number of characters
	int len = text.has_string_value() ? int(text.size()) : 3;	// assume a number is 3 digits
	double obj_size = height/len;
	double threshold_size = intercept + x_coeff * eccentricity + x2_coeff * eccentricity * eccentricity;
	return (obj_size > threshold_size);
}		

long Text_availability::delay(Smart_Pointer<Visual_store_object>, double time_fluctuation)
{
	return long(transduction_delay * time_fluctuation);
}

string Text_availability::get_description() const
{
	ostringstream oss;
	oss << get_property_name() 
		<< ": Quadratically available outside fovea  using height adjusted by length, with intercept " << intercept 
		<< ", linear " << x_coeff << ", and quadratic " << x2_coeff 
		<< " components per degree eccentricity after " << transduction_delay << " ms.";
	return oss.str();
}
