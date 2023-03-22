#include "Invol_ocular_actions.h"
#include "Invol_ocular_processor.h"
#include "../Framework classes/Coordinator.h"
#include "../Visual Classes/Visual_sensory_store.h"
#include "../Framework classes/Output_tee_globals.h"
#include "../Visual Classes/Eye_processor.h"
#include "../Visual Classes/Eye_event_types.h"
#include "../Utility Classes/Geometry.h"
namespace GU = Geometry_Utilities;

#include <cmath>
#include <iostream>

using std::atan2; using std::fabs;
using std::endl;


Invol_ocular_action::Invol_ocular_action(Human_processor * human_ptr_, const Symbol& objname_) :
		Motor_action(human_ptr_, true), objname(objname_)
{
	proc_ptr = human_ptr->get_Invol_ocular_processor_ptr();
	eye_ptr = human_ptr->get_Eye_processor_ptr();
	visual_sensory_store_ptr = human_ptr->get_Visual_sensory_store_ptr();
}

// this object will send itself to the appropriate processor
void Invol_ocular_action::dispatch(long time)
{
	human_ptr->schedule_event(new Motor_Command_Action_event(
		time, 
		human_ptr->get_invol_ocular_ptr(),
		this));
}

Parameter& Invol_ocular_action::get_saccade_intercept() const
{
	return proc_ptr->saccade_intercept;
}	

Parameter& Invol_ocular_action::get_saccade_slope() const
{
	return proc_ptr->saccade_slope;
}	

Parameter& Invol_ocular_action::get_saccade_refractory_period() const
{
	return proc_ptr->saccade_refractory_period;
}	

Parameter& Invol_ocular_action::get_smooth_move_intercept() const
{
	return proc_ptr->smooth_move_intercept;
}	

Parameter& Invol_ocular_action::get_smooth_move_slope() const
{
	return proc_ptr->smooth_move_slope;
}	

Parameter& Invol_ocular_action::get_smooth_move_refractory_period() const
{
	return proc_ptr->smooth_move_refractory_period;
}	

void Invol_ocular_action::compute_movement_features()
{
	// get the current eye position - will be future location if it is in motion
	GU::Point current_eye_location = get_eye_ptr()->get_location();
	// get the object position and save it
	obj_location = visual_sensory_store_ptr->get_object_ptr(objname)->get_location();

	// compute the direction and extent for the eye movement as a polar vector
	move_vector = GU::Polar_vector(current_eye_location, obj_location);
	
	// if the eye is already in position, this move needs to be aborted
	if (move_vector.r < 0.1) {
		move_vector.r = 0.0;	// distance to be moved is really zero
		}
}


// note that dynamic_cast of a pointer whose value is zero results in zero

// return the time required for preparation
// Involuntary Ocular Move is is direction = extent, no style issues
long Invol_ocular_Saccade_action::prepare(long base_time)
{
	if(get_processor_ptr()->get_trace() && Trace_out)
		Trace_out << get_processor_ptr()->processor_info() 
		<< "Prepare Involuntary saccade to " << get_object_name() << endl;
	compute_movement_features(); 

	// compare the eye movement to the previous one
	long feature_preparation_time = 0;
// dk 090807 - no feature programming time
/*
	const Invol_ocular_Saccade_action * ptr = 
		dynamic_cast<const Invol_ocular_Saccade_action *>(get_processor_ptr()->get_previous_ptr());
	long feature_time = get_processor_ptr()->get_feature_time();
	if (ptr) {								// previous is same type of action
		if (fabs(get_move_vector().r - ptr->get_move_vector().r) > 2.0)
			feature_preparation_time += feature_time;	// need to generate r
		if (fabs(get_move_vector().theta - ptr->get_move_vector().theta) > GU_pi/4.0)
			feature_preparation_time += feature_time;	// need to generate theta
		}
	else 
		feature_preparation_time = long(feature_time * 2);				
*/
	return base_time + feature_preparation_time;
}

// return the time at which the final movement is complete
// and send any additional messages in the meantime
long Invol_ocular_Saccade_action::execute(long base_time)
{
	// if no move needs to be made, return no additional movement time, and send no events
	// to the eye processor
	if (get_move_vector().r == 0.0)	// see preparation code
		return base_time;

	long intercept = get_saccade_intercept().get_value();
	double slope = get_saccade_slope().get_double_value();
	double fluctuation = get_processor_ptr()->get_execution_fluctuation();
	long execution_time = long(intercept + get_move_vector().r * slope * fluctuation);
	long movement_completion_time = base_time + execution_time;

	// send the eye movement start event at the current time to the eye
	Coordinator::get_instance().schedule_event(new 
		Eye_Involuntary_Saccade_Start_event(
			base_time, get_eye_ptr(), get_obj_location(), movement_completion_time));

	// send the eye movement end event at the movement_completion_time time to the eye
	Coordinator::get_instance().schedule_event(new 
		Eye_Involuntary_Saccade_End_event(
			movement_completion_time, get_eye_ptr()));
	
	// add on the refractory period before the movement is considered complete
	return movement_completion_time + get_saccade_refractory_period().get_value();
}

// Smooth_moves are assumed to take no preparation time
long Invol_ocular_Smooth_move_action::prepare(long base_time)
{
	compute_movement_features(); 
	if(get_processor_ptr()->get_trace() && Trace_out)
		Trace_out << get_processor_ptr()->processor_info() 
		<< "Prepare Involuntary smooth move to " << get_object_name() << endl;

	return base_time;
}

long Invol_ocular_Smooth_move_action::execute(long base_time)
{
	// if no move needs to be made, return no additional movement time, and send no events
	// to the eye processor
	if (get_move_vector().r == 0.0)	// see preparation code
		return base_time;

	long intercept = get_smooth_move_intercept().get_value();
	double slope = get_smooth_move_slope().get_double_value();
	double fluctuation = get_processor_ptr()->get_execution_fluctuation();
	long execution_time = long(intercept + get_move_vector().r * slope * fluctuation);
	long movement_completion_time = base_time + execution_time;

	// send the eye movement start event at the current time to the eye
	Coordinator::get_instance().schedule_event(new 
		Eye_Involuntary_Smooth_Move_Start_event(
			base_time, get_eye_ptr(), get_obj_location(), movement_completion_time));

	// send the eye movement end event at the movement_completion_time time to the eye
	Coordinator::get_instance().schedule_event(new 
		Eye_Involuntary_Smooth_Move_End_event(
			movement_completion_time, get_eye_ptr()));
	
	return movement_completion_time + get_smooth_move_refractory_period().get_value();
}
