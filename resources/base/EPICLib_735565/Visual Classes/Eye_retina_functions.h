#ifndef EYE_RETINAL_FUNCTIONS_H
#define EYE_RETINAL_FUNCTIONS_H

#include "../Utility Classes/Smart_Pointer.h"
#include "Visual_physical_store.h"
#include "Visual_constants.h"
#include "../Utility Classes/Symbol.h"
#include <string>
#include <sstream>

class Visual_physical_store;
class Visual_physical_object;

/*
Base class for property availability objects.
The available function returns true if the property is available.
The delay function returns a time; it may be called even if the property is not available.
*/
class Availability : public Reference_Counted_Object {
public:
	Availability(const Visual_physical_store& physical_store_, const Symbol& property_name_) :
		physical_store(physical_store_), property_name(property_name_)
		{}
	const Symbol& get_property_name() const 
		{return property_name;}
		
	virtual bool available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation) = 0;
	virtual long delay(Smart_Pointer<Visual_store_object> physobj_ptr, double time_fluctuation) = 0;
	virtual std::string get_description() const = 0;
	static Availability * create(const Visual_physical_store& physical_store, const Parameter_specification& param_spec);

protected:
	const Visual_physical_store& physical_store;
private:
	Symbol property_name;
	Availability();
};

/* Zone availability means the property is all-or-none available within a certain
radius; if it is within the "standard" fovea, it is always available, outside
the "standard" periphery, it is not. Otherwise, it is available if it is within
a property-specific "parafoveal" distance, and has a property-specific delay.
*/
class Zone_availability : public Availability {
public:
	Zone_availability(const Visual_physical_store& physical_store_, const Symbol& property_name_,
		long delay_, double zone_radius_) :
		Availability(physical_store_, property_name_), transduction_delay(delay_), zone_radius(zone_radius_)
		{}
	virtual bool available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation);
	virtual long delay(Smart_Pointer<Visual_store_object> physobj_ptr, double time_fluctuation);
	virtual std::string get_description() const;
	static Availability * create(const Visual_physical_store& physical_store_, const Symbol& property_name_, 
		const Parameter_specification& param_spec, std::istringstream& iss);
private:
	long transduction_delay;
	double zone_radius;
};

/* "Standard" default availabilities based on the LISP EPIC defaults
These are zone availabilities that use the "standard" values for fovea, parafovea, and periphery.
*/
// property is available only in the "standard fovea"
class Fovea_std_zone_availability : public Zone_availability {
public:
	Fovea_std_zone_availability(const Visual_physical_store& physical_store_, const Symbol& property_name_, long delay_ = standard_delay) :
	Zone_availability(physical_store_, property_name_, delay_, standard_fovea_radius)
	{}
};

// property is available also in the "standard parafovea"
class Parafovea_std_zone_availability : public Zone_availability {
public:
	Parafovea_std_zone_availability(const Visual_physical_store& physical_store_, const Symbol& property_name_, long delay_ = standard_delay):
	Zone_availability(physical_store_, property_name_, delay_, standard_parafovea_radius)
	{}
};

// property is available everywhere within the periphery
class Periphery_std_zone_availability : public Zone_availability {
public:
	Periphery_std_zone_availability(const Visual_physical_store& physical_store_, const Symbol& property_name_, long delay_ = standard_delay) :
	Zone_availability(physical_store_, property_name_, delay_, standard_peripheral_radius)
	{}
};

// for all visual spatial relations
class Relation_std_zone_availability : public Periphery_std_zone_availability {
public:
	Relation_std_zone_availability(const Visual_physical_store& physical_store_, const Symbol& property_name_);
};

class Color_std_zone_availability : public Parafovea_std_zone_availability {
public:
	Color_std_zone_availability(const Visual_physical_store& physical_store_);
};

class Shape_std_zone_availability : public Parafovea_std_zone_availability {
public:
	Shape_std_zone_availability(const Visual_physical_store& physical_store_);
};

class Text_std_zone_availability : public Fovea_std_zone_availability {
public:
	Text_std_zone_availability(const Visual_physical_store& physical_store_);
};

// End of "standard" zone availabilities


/* Flat availability means the property is all-or-none available with a certain
probability regardless of where it is outside the fovea.
if it is within the "standard" fovea, it is always available.
*/
class Flat_availability : public Availability {
public:
	Flat_availability(const Visual_physical_store& physical_store_, const Symbol& property_name_,
		long delay_, double probability_) :
		Availability(physical_store_, property_name_), transduction_delay(delay_), probability(probability_)
		{}
	virtual bool available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation);
	virtual long delay(Smart_Pointer<Visual_store_object> physobj_ptr, double time_fluctuation);
	virtual std::string get_description() const;
	static Availability * create(const Visual_physical_store& physical_store_, const Symbol& property_name_, 
		const Parameter_specification& param_spec, std::istringstream& iss);
private:
	long transduction_delay;
	double probability;
};


/* Selector availability means the property is all-or-none available with a certain
probability if it has a certain value, and not otherwise, except 
if it is within the "standard" fovea, it is always available. 
*/
class Selector_availability : public Availability {
public:
	Selector_availability(const Visual_physical_store& physical_store_, const Symbol& property_name_,
		long delay_, Symbol selected_value_, double probability_) :
		Availability(physical_store_, property_name_), transduction_delay(delay_), selected_value(selected_value_), probability(probability_)
		{}
	virtual bool available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation);
	virtual long delay(Smart_Pointer<Visual_store_object> physobj_ptr, double time_fluctuation);
	virtual std::string get_description() const;
	static Availability * create(const Visual_physical_store& physical_store_, const Symbol& property_name_, 
		const Parameter_specification& param_spec, std::istringstream& iss);
private:
	long transduction_delay;
	double probability;
	Symbol selected_value;
};

/* Custom availability provides an arbitrary function for determining availability.
This is intended as an aid to data fitting.
*/
class Custom_availability : public Availability {
public:
	Custom_availability(const Visual_physical_store& physical_store_, const Symbol& property_name_,
		long delay_) :
		Availability(physical_store_, property_name_), transduction_delay(delay_)
		{}
	virtual bool available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation);
	virtual long delay(Smart_Pointer<Visual_store_object> physobj_ptr, double time_fluctuation);
	virtual std::string get_description() const;
	static Availability * create(const Visual_physical_store& physical_store_, const Symbol& property_name_, 
		const Parameter_specification& param_spec, std::istringstream& iss);
private:
	long transduction_delay;
};

class Custom_availability2 : public Availability {
public:
	Custom_availability2(const Visual_physical_store& physical_store_, const Symbol& property_name_,
		long delay_) :
		Availability(physical_store_, property_name_), transduction_delay(delay_)
		{}
	virtual bool available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation);
	virtual long delay(Smart_Pointer<Visual_store_object> physobj_ptr, double time_fluctuation);
	virtual std::string get_description() const;
	static Availability * create(const Visual_physical_store& physical_store_, const Symbol& property_name_, 
		const Parameter_specification& param_spec, std::istringstream& iss);
private:
	long transduction_delay;
};


/*
Linear availability requires that an object size be larger than a value specified
as a linear function extending from the standard fovea radius out to the periphery.
The function specifies the minimum size for an object within the fovea,
and the slope for the function. All units are in degrees VA.
The delay is a flat value for the property.
*/
class Linear_availability : public Availability {
public:
	Linear_availability(const Visual_physical_store& physical_store_, const Symbol& property_name_,
		long delay_, double min_size_, double slope_) :
		Availability(physical_store_, property_name_), transduction_delay(delay_), 
		min_size(min_size_),slope(slope_)
		{Assert(min_size > 0. && slope > 0.);}
	virtual bool available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation);
	virtual long delay(Smart_Pointer<Visual_store_object> physobj_ptr, double time_fluctuation);
	virtual std::string get_description() const;
	static Availability * create(const Visual_physical_store& physical_store_, const Symbol& property_name_, 
		const Parameter_specification& param_spec, std::istringstream& iss);
private:
	long transduction_delay;
	double min_size;
	double slope;
};

/*
Quadratic availability requires that an object size be larger than a value specified
as a 2nd-order polynomial function extending from eccentricity = 0 out to the periphery.
The function is in the form: y = intercept + x_coeff * x + x2_coeff * x^2
The function specifies the minimum size for an object.
All units are in degrees VA.
The delay is a flat value for the property.
*/
class Fixed_quadratic_availability : public Availability {
public:
	Fixed_quadratic_availability(const Visual_physical_store& physical_store_, const Symbol& property_name_,
		long delay_, double intercept_, double x_coeff_, double x2_coeff_) :
		Availability(physical_store_, property_name_), transduction_delay(delay_), 
		intercept(intercept_),x_coeff(x_coeff_), x2_coeff(x2_coeff_)
		{Assert(intercept_ > 0. && x_coeff > 0. && x2_coeff > 0.);}
	virtual bool available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation);
	virtual long delay(Smart_Pointer<Visual_store_object> physobj_ptr, double time_fluctuation);
	virtual std::string get_description() const;
	static Availability * create(const Visual_physical_store& physical_store_, const Symbol& property_name_, 
		const Parameter_specification& param_spec, std::istringstream& iss);
private:
	long transduction_delay;
	double intercept;
	double x_coeff;
	double x2_coeff;
};

/*
Quadratic availability requires that an object size plus a Normal fluctuation be larger than a value specified
as a 2nd-order polynomial function extending from eccentricity = 0 out to the periphery.
The object is available if (object_size + fluctuation) > intercept + x_coeff * x + x2_coeff * x^2
where fluctuation is Normal(0., coefvar * object_size)
If ecc < zone, then always available.
All units are in degrees VA.
The delay is a flat value for the property.
*/
class Quadratic_availability : public Availability {
public:
	Quadratic_availability(const Visual_physical_store& physical_store_, const Symbol& property_name_,
		long delay_, double zone_, double coefvar_, double intercept_, double x_coeff_, double x2_coeff_) :
		Availability(physical_store_, property_name_), transduction_delay(delay_), zone(zone_), coefvar(coefvar_),
		intercept(intercept_),x_coeff(x_coeff_), x2_coeff(x2_coeff_)
		{Assert(coefvar > 0. && intercept_ >= 0. && x_coeff >= 0. && x2_coeff >= 0.);}
	virtual bool available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation);
	virtual long delay(Smart_Pointer<Visual_store_object> physobj_ptr, double time_fluctuation);
	virtual std::string get_description() const;
	static Availability * create(const Visual_physical_store& physical_store_, const Symbol& property_name_, 
		const Parameter_specification& param_spec, std::istringstream& iss);
private:
	long transduction_delay;
	double zone;		// if eccentricity less than this, always available
	double coefvar;
	double intercept;
	double x_coeff;
	double x2_coeff;
};



/*
Fixed exponential availability requires that an object size be larger than a value specified
as exponential function extending from eccentricity = 0 out to the periphery.
The function is in the form: y = coef *  base^(expon * x)
The function specifies the minimum size for an object.
All units are in degrees VA.
The delay is a flat value for the property.
*/
class Fixed_exponential_availability : public Availability {
public:
	Fixed_exponential_availability(const Visual_physical_store& physical_store_, const Symbol& property_name_,
		long delay_, double coeff_, double expon_) :
		Availability(physical_store_, property_name_), transduction_delay(delay_), 
		coeff(coeff_), expon(expon_)
		{Assert(coeff > 0. && expon > 0.);}
	virtual bool available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation);
	virtual long delay(Smart_Pointer<Visual_store_object> physobj_ptr, double time_fluctuation);
	virtual std::string get_description() const;
	static Availability * create(const Visual_physical_store& physical_store_, const Symbol& property_name_, 
		const Parameter_specification& param_spec, std::istringstream& iss);
private:
	long transduction_delay;
	double coeff;
	double expon;
};

/*
Exponential availability requires that an object size plus a Normal fluctuation 
be larger than a value specified as exponential function extending from eccentricity = 0 out to the periphery.
The object is available if (object_size + fluctuation) > coef *  exp(expon * x)
where fluctuation is Normal(0., coefvar * object_size)
For foveal objects (ecc < 1) and size > .1 DVA, always available.
All units are in degrees VA.
The delay is a flat value for the property.
*/
class Exponential_availability : public Availability {
public:
	Exponential_availability(const Visual_physical_store& physical_store_, const Symbol& property_name_,
		long delay_, double coefvar_, double coeff_, double expon_) :
		Availability(physical_store_, property_name_), transduction_delay(delay_), 
		coefvar(coefvar_), coeff(coeff_), expon(expon_)
		{Assert(coefvar > 0. && coeff > 0. && expon > 0.);}
	virtual bool available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation);
	virtual long delay(Smart_Pointer<Visual_store_object> physobj_ptr, double time_fluctuation);
	virtual std::string get_description() const;
	static Availability * create(const Visual_physical_store& physical_store_, const Symbol& property_name_, 
		const Parameter_specification& param_spec, std::istringstream& iss);
private:
	long transduction_delay;
	double coefvar;
	double coeff;
	double expon;
};







// These are specific availability functions that use the general functions

/* Color availability. */
class Color_exp_availability : public Fixed_exponential_availability {
public:
	Color_exp_availability(const Visual_physical_store& physical_store_, long delay_ = standard_delay);
};

/*
Color_quad_availability uses a Fixed_quadratic_availability model, but special-cases "Red" if 
it is not available. All units are in degrees VA.
The delay is a flat value for the property.
*/

class Color_quad_availability : public Fixed_quadratic_availability {
public:
	Color_quad_availability(const Visual_physical_store& physical_store_, long delay_ = standard_delay);
	virtual bool available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation);
private:
	double red_min_size;
};



/* Shape availability */

class Shape_quad_availability : public Fixed_quadratic_availability {
public:
	Shape_quad_availability(const Visual_physical_store& physical_store_, long delay_ = standard_delay);
};

class Shape_exp_availability : public Fixed_exponential_availability {
public:
	Shape_exp_availability(const Visual_physical_store& physical_store_, long delay_ = standard_delay);
};

/* Text availability */


class Text_availability : public Availability {
public:
	Text_availability(const Visual_physical_store& physical_store_, long delay_ = standard_delay);
	virtual bool available(Smart_Pointer<Visual_store_object> physobj_ptr, double eccentricity_fluctuation);
	virtual long delay(Smart_Pointer<Visual_store_object> physobj_ptr, double time_fluctuation);
	virtual std::string get_description() const;
private:
	long transduction_delay;
	double intercept;
	double x_coeff;
	double x2_coeff;
};


#endif
