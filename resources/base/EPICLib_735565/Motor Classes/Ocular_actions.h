#ifndef OCULAR_ACTIONS_H
#define OCULAR_ACTIONS_H

/*
The Ocular_action classes encapsulate how a particular type of voluntary ocular movement is 
prepared and executed. Each subclass defines what the preparation time is in relation
to the previously prepared movement, and the execution time for the movement.
The execute function is responsible for sending messages to the device and
any other special messages.

The controlling ocular motor processor is responsible for sequencing the movements
through waiting, preparation, ready, and executing stages. For each commanded movement,
it will create a new Ocular_action object to store the movement information, and then
delete it when it is no longer needed.
*/

#include "Motor_action.h"
#include "../Utility Classes/Geometry.h"
namespace GU = Geometry_Utilities;
#include "../Utility Classes/Symbol.h"

// forward declaration
class Ocular_processor;
class Eye_processor;
class Visual_perceptual_store;
class Auditory_perceptual_store;

// Abstract base class
// the Voluntary ocular actions differ only in the final states for the eye processor,
// so almost everything can be computed in the base class
class Ocular_action : public Motor_action {
public:
	// "virtual constructor" static method to construct appropriate motor action
	// given list of action arguments; throws exception if arguments invalid
	static Smart_Pointer<Motor_action> create(Human_processor * human_ptr, Symbol_list_t arguments, bool execute_when_prepared);

	// this object will send itself to the appropriate processor at the specified time
	virtual void dispatch(long time);

	virtual long prepare(long base_time);

	Ocular_processor * get_processor_ptr() const
		{return proc_ptr;}
	Eye_processor * get_eye_ptr() const
		{return eye_ptr;}
	Visual_perceptual_store * get_perceptual_space_ptr() const
		{return visual_perceptual_store_ptr;}
//	GU::Point get_obj_location() const;	// the location of the visual, auditory, or named location
//	const Symbol& get_objname() const	//  the name of the visual, auditory, or named location
//		{return objname;}
	
//		{return obj_location;}
//	bool get_actual_object() const;
//		{return actual_object;}
protected:
	// look up and return the physical name for the taget object from its source
	Symbol get_target_object_device_name() const;
	GU::Point get_target_object_location() const;
	long compute_execution_time(long base_time);
	// regular constructor sets processor pointer, target object, execute flag
	Ocular_action(Human_processor * human_ptr_, const Symbol& objname, bool execute_when_prepared);
	
private:
	Ocular_processor * proc_ptr;	// pointer to the controlling motor processor
	Eye_processor * eye_ptr;	// pointer to the connected eye
	Visual_perceptual_store * visual_perceptual_store_ptr;	// pointer to the perceptual store
	Auditory_perceptual_store * auditory_perceptual_store_ptr;	// pointer to the perceptual store
	enum Object_source_e {NONE, NAMED_LOCATION, VISUAL_OBJECT, AUDITORY_SOURCE};
	Object_source_e object_source;
//	bool actual_object;	// true if object name specified, false if named location specified
	Symbol objname;
	GU::Point obj_location;
	GU::Polar_vector move_vector;
};

// this just sets the modes for the eye/involuntary ocular processor signals for reflex and centering
// it is part of the Ocular actions because the mode-setting commands are under cognitive control
class Ocular_Mode_action : public Ocular_action {
public:
	Ocular_Mode_action(Human_processor * human_ptr_, 
		const Symbol_list_t& arguments, bool execute_when_prepared);
	virtual long prepare(long base_time);
	virtual long execute(long base_time);
private:
	Symbol command;
	Symbol system;
};


class Ocular_Move_action : public Ocular_action {
public:
	Ocular_Move_action(Human_processor * human_ptr_, const Symbol& objname_, bool execute_when_prepared) :
		Ocular_action(human_ptr_, objname_, execute_when_prepared)
		{}
	virtual long execute(long base_time);
};

// this action always executes when prepared
// Send_to_motor Ocular Look_for method_name tag_name p v p v ...
// results in eye on object and (Tag method_name object tag_name) in PPS database
class Ocular_Look_for_action : public Ocular_action {
public:
	Ocular_Look_for_action(Human_processor * human_ptr_, const Symbol_list_t& arguments, bool execute_when_prepared);
	virtual long prepare(long base_time);
	virtual long execute(long base_time);
	virtual void finish();
private:
	Symbol method_name;
	Symbol tag_name;
	Symbol_list_t pv_list;
	Symbol object_name;
	GU::Point obj_location;
	
};



#endif
