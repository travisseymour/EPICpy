#include "Ocular_actions.h"
#include "Ocular_processor.h"
#include "../Framework classes/Coordinator.h"
#include "../Architecture Classes/Cognitive_processor.h"
#include "../Visual Classes/Visual_perceptual_store.h"
#include "../Auditory Classes/Auditory_physical_store.h"
#include "../Auditory Classes/Auditory_perceptual_store.h"
#include "../Framework classes/Output_tee_globals.h"
#include "../Epic_standard_symbols.h"
#include "../Visual Classes/Eye_processor.h"
#include "../Visual Classes/Eye_event_types.h"
#include "../Framework classes/Device_event_types.h"	// to allow device to eye-track
#include "../Framework classes/Device_processor.h"	// to allow conversion of Device_processor * to Processor * in schedule_event
#include "../Utility Classes/Random_utilities.h"
#include "../Utility Classes/Symbol_utilities.h"
#include "../Utility Classes/Geometry.h"
namespace GU = Geometry_Utilities;

#include <cmath>
#include <iostream>

using std::string;
using std::atan2; using std::fabs;
using std::endl;

class Unknown_ocular_target : public Epic_exception {
public:
Unknown_ocular_target(const Symbol& obj_name)
	{
		msg = "*** Error: Attempt to move eyes to unknown store object: " + obj_name.str();
	}
};

// this "virtual constructor" method returns a pointer to the created object
// based on the contents of the list of motor command parameters
// or zero if no object was created because the parameters are invalid
Smart_Pointer<Motor_action> Ocular_action::create(Human_processor * human_ptr, 
	Symbol_list_t arguments, bool execute_when_prepared)
{	
	if(arguments.size() < 2)
		return 0;
	
	const Symbol style = arguments.front();
	arguments.pop_front();
	if(style == Move_c) {
		return new Ocular_Move_action(human_ptr, arguments.front(), execute_when_prepared);
		}
	else if(style == Look_for_c) {
		return new Ocular_Look_for_action(human_ptr, arguments, execute_when_prepared);
		}
	else if(style == Set_mode_c)
		return new Ocular_Mode_action(human_ptr, arguments, execute_when_prepared);
	else
		return 0;
}

Ocular_action::Ocular_action(Human_processor * human_ptr_, const Symbol& objname_, bool execute_when_prepared) :
		Motor_action(human_ptr_, execute_when_prepared), objname(objname_)
{
	proc_ptr = human_ptr->get_Ocular_processor_ptr();
	eye_ptr = human_ptr->get_Eye_processor_ptr();
	visual_perceptual_store_ptr = human_ptr->get_Visual_perceptual_store_ptr();
	auditory_perceptual_store_ptr = human_ptr->get_Auditory_perceptual_store_ptr();
	// if the objname_ is Nil, then do not try to locate it ...
	if(objname == Nil_c) {
		object_source = NONE;
		return;
		}
	
	// determine the source of the object and save it
	// is the target a named location?
	bool found;
	human_ptr->get_Cognitive_processor_ptr()->get_named_location(objname, found); // awkward - no is_present?
	if(found)
		object_source = NAMED_LOCATION;
	else if(visual_perceptual_store_ptr->is_present(objname))
		object_source = VISUAL_OBJECT;
	else if(auditory_perceptual_store_ptr->is_sound_present(objname))
//	else if(auditory_perceptual_store_ptr->is_stream_present(objname))
		object_source = AUDITORY_SOURCE;
	else
		throw Unknown_ocular_target(objname);
}

// this object will send itself to the appropriate processor
void Ocular_action::dispatch(long time)
{
	human_ptr->schedule_event(new Motor_Command_Action_event(
		time, 
		human_ptr->get_ocular_ptr(),
		this));
}

long Ocular_action::compute_execution_time(long base_time)
{
	if (move_vector.r == 0.0)
		return base_time;
		
	long intercept = proc_ptr->saccade_intercept.get_value();
	double slope = proc_ptr->saccade_slope.get_double_value();
	double fluctuation = proc_ptr->get_execution_fluctuation();
	long execution_time = long(intercept + move_vector.r * slope * fluctuation);
	return base_time + execution_time;
}

// this preparation can be shared by all voluntary ocular actions
long Ocular_action::prepare(long base_time)
{
	// get the current eye position - will be future location if it is in motion
	GU::Point current_eye_location = eye_ptr->get_location();
	obj_location = get_target_object_location();
		
/*			
	if(actual_object) {
		// get the object position and save it; give visual object priority
		if(visual_perceptual_store_ptr->is_present(objname))
			obj_location = visual_perceptual_store_ptr->get_object_ptr(objname)->get_location();
		// auditory sources have locations, not sounds
		else if(auditory_perceptual_store_ptr->is_stream_present(objname))
			obj_location = auditory_perceptual_store_ptr->get_stream_ptr(objname)->get_location();
		else 
			throw Unknown_ocular_target(objname);
		}
*/
	// compute the direction and extent for the eye movement as a polar vector
	move_vector = GU::Polar_vector(current_eye_location, obj_location);
	
	// no - must allow a dummy move to an object already in view, but no change here - 2/22/08 DK
	// if the eye is already in position, this move needs to be aborted
	if (move_vector.r < 0.1) {
		move_vector.r = 0.0;	// distance to be moved is really zero
		return base_time;
		}
	// compare the eye movement to the previous one
	long feature_preparation_time = 0;
// dk 090807 - no feature programming time charge for r, theta
/*
	const Ocular_action * ptr = 
		dynamic_cast<const Ocular_action *>(get_processor_ptr()->get_previous_ptr());
	long feature_time = get_processor_ptr()->get_feature_time();
	if (ptr) {								// previous is same type of action
		if (fabs(move_vector.r - ptr->move_vector.r) > 2.0)
			feature_preparation_time += feature_time;	// need to generate r
		if (fabs(move_vector.theta - ptr->move_vector.theta) > GU_pi/4.0)
			feature_preparation_time += feature_time;	// need to generate theta
		}
	else 
		feature_preparation_time = long(feature_time * 2);
*/

	return base_time + feature_preparation_time;
}

// look up and return the location of the target object from its source
GU::Point Ocular_action::get_target_object_location() const
{
	GU::Point result;
	switch(object_source) {
		case NAMED_LOCATION: {
			bool found;	// not used
			result = human_ptr->get_Cognitive_processor_ptr()->get_named_location(objname, found); // awkward - no is_present?
			break;
			}
		case VISUAL_OBJECT:
			result = visual_perceptual_store_ptr->get_object_ptr(objname)->get_location();
			break;
		case AUDITORY_SOURCE:
		//	result = auditory_perceptual_store_ptr->get_stream_ptr(objname)->get_location();
			result = auditory_perceptual_store_ptr->get_sound_ptr(objname)->get_location();
			break;
		default:	// shouldn't happen
			throw Unknown_ocular_target(objname);
			break;
		}
	return result;
}

// look up and return the physical name for the target object from its source
Symbol Ocular_action::get_target_object_device_name() const
{
	Symbol result;
	switch(object_source) {
		case NAMED_LOCATION:
			result = objname;	// same as orginal name
			break;
		case VISUAL_OBJECT:
			result = human_ptr->get_Eye_processor_ptr()->get_name_map().get_physical_name(objname);
			break;
		case AUDITORY_SOURCE:	// notice the difference between location of name_map
			result = human_ptr->get_Auditory_physical_store_ptr()->get_name_map().get_physical_name(objname);
			break;
		default:
			throw Unknown_ocular_target(objname);
			break;
		}
	return result;
}

Ocular_Mode_action::Ocular_Mode_action(Human_processor * human_ptr_, 
	const Symbol_list_t& arguments, bool execute_when_prepared) :
		Ocular_action(human_ptr_, Nil_c, execute_when_prepared)
{
	// arguments in the form Enable/Disable Centering/Reflex
	command = arguments.front();
	system = arguments.back();	// assuming only two
	
	
	if(command != Enable_c && command != Disable_c)
		throw Motor_action_exception(human_ptr, "Invalid command in Set_mode action", command);
		
	if(system != Centering_c && system != Reflex_c)
		throw Motor_action_exception(human_ptr, "Invalid system in Set_mode action", system);
}

// a mode action has a constant preparation time based on 2 features
// purely speculative - but command is one feature, system is another
long Ocular_Mode_action::prepare(long base_time)
{
	long feature_preparation_time = long(get_processor_ptr()->get_feature_time() * 2);				

	return base_time + feature_preparation_time;
}

// return the time at which the action is complete
// assume - purely speculative, that the mode exection takes a burst time
long Ocular_Mode_action::execute(long base_time)
{
	long movement_completion_time = base_time + get_processor_ptr()->get_burst_time();
	Assert(command == Enable_c || command == Disable_c);
	Assert(system == Centering_c || system == Reflex_c);
	
	if(get_processor_ptr()->get_trace() && Trace_out)
		Trace_out << get_processor_ptr()->processor_info() << "Mode Command: " 
		<< command << ' ' << system << endl;

	bool state = (command == Enable_c) ? true : false;
	if(system == Centering_c) {
		get_eye_ptr()->set_centering_enabled(state);
		}
	else if(system == Reflex_c) {
		get_eye_ptr()->set_reflex_enabled(state);
		get_eye_ptr()->set_auditory_reflex_enabled(state);
		}
	
	return movement_completion_time;
}




// return the time at which the final movement is complete
// and send any additional messages in the meantime
long Ocular_Move_action::execute(long base_time)
{
	long movement_completion_time = compute_execution_time(base_time);

	// if no move needs to be made, return no additional movement time, and send no events
	// to the eye processor
	// change made so that a move to the same object as current fixated one signals the eye 
	// as if a zero-length eye movement has been made.  DK 2/22/08
//	if (movement_completion_time == base_time)	// see preparation code
//		return base_time;

	// send the eye movement start event at the current time to the eye
	Coordinator::get_instance().schedule_event(new 
		Eye_Voluntary_Saccade_Start_event(
			base_time, get_eye_ptr(), get_target_object_location(), movement_completion_time));
			
	// send the eye movement end event at the movement_completion_time time to the eye
	// set centering on, reflexes off
	Coordinator::get_instance().schedule_event(new 
		Eye_Voluntary_Saccade_End_event(
			movement_completion_time, get_eye_ptr(), true, false));
			
	// do not signal the device if the e.m. is zero length  DK 2/22/08
	if (movement_completion_time == base_time)	// see preparation code
		return base_time;
	
	// signal the device (to allow eye tracking)
	// use either the actual object name or the named location name
	Symbol obj_device_name = get_target_object_device_name();
/*	Symbol obj_device_name = (get_actual_object()) ?
		human_ptr->get_Eye_processor_ptr()->get_name_map().get_physical_name(get_objname())
		:
		get_objname();
*/
	Coordinator::get_instance().schedule_event(new 
		Device_Eyemovement_Start_event(
			base_time, human_ptr->get_device_ptr(), obj_device_name, get_target_object_location()));

	Coordinator::get_instance().schedule_event(new 
		Device_Eyemovement_End_event(
			movement_completion_time, human_ptr->get_device_ptr(), obj_device_name, get_target_object_location()));
			
	return movement_completion_time;
}

/* GOMS Look_for operator implementation */
// Send_to_motor Ocular Look_for method_name tag_name p v p v ...
// results in eye on object and (Tag method_name object tag_name) in PPS database
Ocular_Look_for_action::Ocular_Look_for_action(Human_processor * human_ptr, const Symbol_list_t& arguments, bool execute_when_prepared) :
	Ocular_action(human_ptr, Symbol("Unknown"), execute_when_prepared), pv_list(arguments)
{
	// check for correct length
	if(!((pv_list.size() >= 4) && ((pv_list.size() % 2) == 0)))
		throw Motor_action_exception(human_ptr, " Ocular_Look_for: ", pv_list);
		
	method_name = pv_list.front();
	pv_list.pop_front();
	tag_name = pv_list.front();
	pv_list.pop_front();
	// keep remainder as list of property name and value pairs
}

const long Look_for_preparation_time_c = 200;

long Ocular_Look_for_action::prepare(long base_time)
{
	// find and store the sought-for object's psychological name using the property list
	Visual_physical_store * visual_store_ptr = human_ptr->get_Visual_physical_store_ptr();
	Symbol_list_t objects = visual_store_ptr->find_all(pv_list);
	if(objects.empty()) {
		/* no object there to be found */
		object_name = Absent_c;
		return base_time + Look_for_preparation_time_c;
		}
	else if(objects.size() == 1) {
		object_name = objects.front();
		}
	else {
		// pick one at random
		object_name = get_nth_Symbol(objects, random_int(int(objects.size())));
		}
		
	// store the object location as known physically
	obj_location = visual_store_ptr->get_object_ptr(object_name)->get_location();
	
	// unconditionally, the feature preparation time is a constant
	
	return base_time + Look_for_preparation_time_c;
}

const long Look_for_execution_time_c = 1000;

// return the time at which the final movement is complete
// and send any additional messages in the meantime
long Ocular_Look_for_action::execute(long base_time)
{
	long movement_completion_time = base_time + Look_for_execution_time_c;
	// if no object there to be found, skip the actual eye movement, but take the full time
	if(object_name == Absent_c)
		return movement_completion_time;

	// send the eye movement start event at the current time to the eye
	Coordinator::get_instance().schedule_event(new 
		Eye_Voluntary_Saccade_Start_event(
			base_time, get_eye_ptr(), obj_location, movement_completion_time));

	// send the eye movement end event at the movement_completion_time time to the eye
	// set centering on, reflexes off
	Coordinator::get_instance().schedule_event(new 
		Eye_Voluntary_Saccade_End_event(
			movement_completion_time, get_eye_ptr(), true, false));
			
	
	return movement_completion_time;
}


// Inform cognitive processor of object identity using the supplied tag
void Ocular_Look_for_action::finish()
{
	// if the object name is not absent, get the psychological name for the object and store that
	if(object_name != Absent_c) {
		const Symbol& psych_name = get_eye_ptr()->get_name_map().get_psychological_name(object_name);
		human_ptr->get_Cognitive_processor_ptr()->add_clause(Clause (Tag_c, method_name, psych_name, tag_name));
		}
	else {
		human_ptr->get_Cognitive_processor_ptr()->add_clause(Clause (Tag_c, method_name, Absent_c, tag_name));
		}
}
