#include "Auditory_perceptual_processor.h"
#include "Auditory_event_types.h"
#include "Auditory_sensory_store.h"
#include "../Framework classes/Auditory_encoder_base.h"
#include "../Framework classes/Epic_exception.h"
#include "../Framework classes/Output_tee_globals.h"
#include "../Epic_standard_symbols.h"

#include <string>
#include <iostream>
#include <sstream>
//#include <algorithm>
//#include <functional>
#include <typeinfo>

using namespace std;


/*** Exception classes ***/
// this is a user-interpretable error
class Unknown_perceptual_property : public Epic_exception {
public:
Unknown_perceptual_property(Processor * proc_ptr, const Symbol& propname)
	{
		msg = proc_ptr->processor_info() + 
		"Unknown perceptual property received: " + propname.str();
	}
};

const Symbol Category_c ("Category");

void Auditory_perceptual_processor::setup()
{
	recoding_times[Pitch_c] = 100;
	recoding_times[Loudness_c] = 100;
	recoding_times[Timbre_c] = 100;
	recoding_times[Content_c] = 100;
	recoding_times[Gender_c] = 100;
	recoding_times[Speaker_c] = 100;
	recoding_times[Category_c] = 100; // gets added to duration ...
	recoding_times[Start_time_c] = 60;
	recoding_times[End_time_c] = 60;
	add_parameter(appearance_delay);
	add_parameter(disappearance_delay);
	add_parameter(location_delay);
	add_parameter(recoded_location_delay);
//	add_parameter(property_time_fluctuation);
	add_parameter(recoding_time_fluctuation);
	add_parameter(transient_decay_time);
	add_parameter(recoding_failure_rate1);
	
	initialize_recodings();
}

// set overall state
void Auditory_perceptual_processor::initialize()
{
	Human_subprocessor::initialize();
}

void Auditory_perceptual_processor::set_auditory_encoder_ptr(Auditory_encoder_base * auditory_encoder_ptr_)
{
	auditory_encoder_ptr = auditory_encoder_ptr_;
}

//  parameter modifiers
// specification contains <property> <time>
void Auditory_perceptual_processor::set_parameter(const Parameter_specification& param_spec)
{
	if(param_spec.parameter_name == "Recoding_time") {
		istringstream iss(param_spec.specification);
		// first term is property name
		string property_name;
		iss >> property_name;
		if(!iss)
			Parameter::throw_parameter_error("Unable to read property name in parameter specification", param_spec);
		Symbol prop_name(property_name);
	// second term is delay value
		long delay;
		iss >> delay;
		if(!iss)
			Parameter::throw_parameter_error("Unable to read recoding delay in parameter specification", param_spec);
		recoding_times[prop_name] = delay;
		}
	else {
		Human_subprocessor::set_parameter(param_spec);
		}
}

void Auditory_perceptual_processor::describe_parameters(Output_tee& ot) const
{
	Human_subprocessor::describe_parameters(ot);

	ot<< "Recoding_time:" << endl;
	for(Recoding_times_t::const_iterator it = recoding_times.begin(); it != recoding_times.end(); ++it) {
		ot << "    " << it->first << ": recoded after " << it->second << " ms." << endl;
		}
}

void Auditory_perceptual_processor::accept_event(const Auditory_event * event_ptr)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << typeid(*event_ptr).name() << " received" << endl;
	broadcast_to_recorders(event_ptr);
	// tell the event to handle itself with itself!
	event_ptr->handle_self(this);
}

void Auditory_perceptual_processor::accept_event(const Stop_event *)
{
//	perceptual_space.display_contents(Normal_out);
}

void Auditory_perceptual_processor::create_stream(const Symbol& name, double pitch_, double loudness_, GU::Point location)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "create stream " << name << endl;
			
	// transmit the event forward to the next store
	schedule_event(new Auditory_Stream_Create_event(
		get_time() + appearance_delay.get_value(), get_human_ptr()->get_auditory_perceptual_store_ptr(),
		name, pitch_, loudness_, location));
}

void Auditory_perceptual_processor::destroy_stream(const Symbol& name)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "destroy stream " << name << endl;

	// transmit the event forward to the next store
	schedule_event(new Auditory_Stream_Destroy_event(
		get_time() + disappearance_delay.get_value(), get_human_ptr()->get_auditory_perceptual_store_ptr(),
		name));
}

// simply update the location stored with the object - 
GU::Point Auditory_perceptual_processor::set_stream_location(const Symbol& name, GU::Point location)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "set stream " << name
			<< " location to " << location << endl;
			
	
	// transmit the event forward to the next store
	schedule_event(new Auditory_Stream_Set_Location_event(
		get_time() + location_delay.get_value(), get_human_ptr()->get_auditory_perceptual_store_ptr(),
		name, location));
	return location;
}

// simply update the pitch stored with the object - 
double Auditory_perceptual_processor::set_stream_pitch(const Symbol& name, double pitch)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "set stream " << name
			<< " pitch to " << pitch << endl;
			
	
	// transmit the event forward to the next store
	schedule_event(new Auditory_Stream_Set_Pitch_event(
		get_time() + location_delay.get_value(), get_human_ptr()->get_auditory_perceptual_store_ptr(),
		name, pitch));
	return pitch;
}

double Auditory_perceptual_processor::set_stream_loudness(const Symbol& name, double loudness)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "set stream " << name
			<< " loudness to " << loudness << endl;
			
	
	// transmit the event forward to the next store
	schedule_event(new Auditory_Stream_Set_Loudness_event(
		get_time() + location_delay.get_value(), get_human_ptr()->get_auditory_perceptual_store_ptr(),
		name, loudness));
	return loudness;
}

// simply update the location stored with the object - 
GU::Size Auditory_perceptual_processor::set_stream_size(const Symbol& name, GU::Size size)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "set stream " << name
			<< " size to " << size << endl;
			
	
	// transmit the event forward to the next store
	schedule_event(new Auditory_Stream_Set_Size_event(
		get_time() + location_delay.get_value(), get_human_ptr()->get_auditory_perceptual_store_ptr(),
		name, size));
	return size;
}

Symbol Auditory_perceptual_processor::set_stream_property(const Symbol& object_name, const Symbol& property_name, const Symbol& property_value)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "set stream " << object_name 
			<< " property " << property_name << " to " << property_value << endl;

	// look up recoding time - no substantive recoding here - MUST FIX!
	Recoding_times_t::iterator it = recoding_times.find(property_name);
	if(it == recoding_times.end())
		throw Unknown_perceptual_property(this, property_name);
	long recoding_time = it->second;
	recoding_time = long(recoding_time * recoding_time_fluctuation.get_double_value());
	// transmit the event forward to the next store
	schedule_event(new Auditory_Stream_Set_Property_event(
		get_time() + recoding_time, get_human_ptr()->get_auditory_perceptual_store_ptr(),
		object_name, property_name, property_value));
	return property_value;
}

//void Auditory_perceptual_processor::make_new_sound_start(const Symbol& sound_name, const Symbol& stream_name, long time_stamp, 
void Auditory_perceptual_processor::make_new_sound_start(const Symbol& sound_name, const Symbol& stream_name, long time_stamp, GU::Point location,
	const Symbol& timbre, double loudness, long intrinsic_duration)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "make sound " << sound_name << " start" << endl;
	long appearance_delay_time = appearance_delay.get_value();
	
	// if an encoder has been set, apply it to the location
	if(auditory_encoder_ptr) {
		GU::Point new_location = auditory_encoder_ptr->recode_location(location);
		location = new_location;
		appearance_delay_time = recoded_location_delay.get_value();
		}

	// transmit the start event forward to the next store
	schedule_event(new Auditory_Sound_Start_event(
		get_time() + appearance_delay_time, get_human_ptr()->get_auditory_perceptual_store_ptr(),
		sound_name, stream_name, time_stamp, location, timbre, loudness, intrinsic_duration));
	// create and send a transient property forward - Onset arrives at same time, then disappears
	schedule_event(new Auditory_Sound_Set_Property_event(
		get_time() + appearance_delay_time, get_human_ptr()->get_auditory_perceptual_store_ptr(),
		sound_name, Detection_c, Onset_c));
	// arrange to remove the transient after its delay
	schedule_event(new Auditory_Sound_Set_Property_event(
		get_time() + appearance_delay_time + transient_decay_time.get_value(), get_human_ptr()->get_auditory_perceptual_store_ptr(),
		sound_name, Detection_c, Nil_c));
}

//void Auditory_perceptual_processor::make_new_speech_start(const Symbol& sound_name, const Symbol& stream_name, long time_stamp, 
//		const Symbol& content, const Symbol& speaker_gender, const Symbol& speaker_id, double loudness, long duration)
void Auditory_perceptual_processor::make_new_speech_start(const Speech_word& word)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "make speech sound " << word.name << " start" << endl;
			
	// transmit the start event forward to the next store
/*	schedule_event(new Auditory_Speech_Start_event(
		get_time() + appearance_delay.get_value(), get_human_ptr()->get_auditory_perceptual_store_ptr(),
		sound_name, stream_name, time_stamp, content, speaker_gender, speaker_id, loudness, duration)); */
	schedule_event(new Auditory_Speech_Start_event(
		get_time() + appearance_delay.get_value(), get_human_ptr()->get_auditory_perceptual_store_ptr(),
		word));

	// create and send a transient property forward - Onset arrives at same time, then disappears
	schedule_event(new Auditory_Sound_Set_Property_event(
		get_time() + appearance_delay.get_value(), get_human_ptr()->get_auditory_perceptual_store_ptr(),
		word.name, Detection_c, Onset_c));
	// arrange to remove the transient after its delay
	schedule_event(new Auditory_Sound_Set_Property_event(
		get_time() + appearance_delay.get_value() + transient_decay_time.get_value(), get_human_ptr()->get_auditory_perceptual_store_ptr(),
		word.name, Detection_c, Nil_c));

	// send categorized content forward after a delay, but only if a recoding is found
	Category_recodings_t::iterator category_it = category_recodings.find(word.content);
	Recoding_times_t::iterator time_it = recoding_times.find(Category_c);
	if(category_it != category_recodings.end() && time_it != recoding_times.end()) {
		Symbol recoded_content = category_it->second;
		long property_recoding_time = time_it->second;
//		long recoding_time = long((property_recoding_time + duration) * recoding_time_fluctuation.get_double_value());
		long recoding_time = long((property_recoding_time) * recoding_time_fluctuation.get_double_value()); // dk 8/11/11 to speed things up

		schedule_event(new Auditory_Sound_Set_Property_event(
			get_time() + recoding_time, get_human_ptr()->get_auditory_perceptual_store_ptr(),
			word.name, Category_c, recoded_content));
		}
	
}

const Symbol Digit_c("Digit");
const Symbol Masker_callsign_c("Masker_callsign");
const Symbol Target_callsign_c("Target_callsign");
const Symbol Callsign_c("Callsign");

void Auditory_perceptual_processor::initialize_recodings()
{
	// classify content by look-up
	category_recodings.insert(make_pair(Symbol("arrow"),   Masker_callsign_c));
	category_recodings.insert(make_pair(Symbol("baron"),   Target_callsign_c));
	category_recodings.insert(make_pair(Symbol("charlie"), Masker_callsign_c));
	category_recodings.insert(make_pair(Symbol("eagle"),   Masker_callsign_c));
	category_recodings.insert(make_pair(Symbol("hopper"),  Masker_callsign_c));
	category_recodings.insert(make_pair(Symbol("laker"),   Masker_callsign_c));
	category_recodings.insert(make_pair(Symbol("ringo"),   Masker_callsign_c));
	category_recodings.insert(make_pair(Symbol("tiger"),   Masker_callsign_c));
	category_recodings.insert(make_pair(Symbol("tiger"),   Masker_callsign_c));
	category_recodings.insert(make_pair(Symbol("Darkstar"), Callsign_c));
	category_recodings.insert(make_pair(Symbol("Chalice"), Callsign_c));
	category_recodings.insert(make_pair(Symbol("Victor"), Callsign_c));
	category_recodings.insert(make_pair(Symbol("Tango"), Callsign_c));

	category_recodings.insert(make_pair(Blue_c, Color_c));
	category_recodings.insert(make_pair(Green_c, Color_c));
	category_recodings.insert(make_pair(Red_c, Color_c));
	category_recodings.insert(make_pair(Yellow_c, Color_c));
	
	category_recodings.insert(make_pair(Symbol(1), Digit_c));
	category_recodings.insert(make_pair(Symbol(2), Digit_c));
	category_recodings.insert(make_pair(Symbol(3), Digit_c));
	category_recodings.insert(make_pair(Symbol(4), Digit_c));
	category_recodings.insert(make_pair(Symbol(5), Digit_c));
	category_recodings.insert(make_pair(Symbol(6), Digit_c));
	category_recodings.insert(make_pair(Symbol(7), Digit_c));
	category_recodings.insert(make_pair(Symbol(8), Digit_c));
	category_recodings.insert(make_pair(Symbol(9), Digit_c));

	category_recodings.insert(make_pair(Square_c, Shape_c));
	category_recodings.insert(make_pair(Diamond_c, Shape_c));
	category_recodings.insert(make_pair(Circle_c, Shape_c));
//	category_recodings.insert(make_pair(Arrow_c, Shape_c));
	category_recodings.insert(make_pair(Up_Arrow_c, Shape_c));
	category_recodings.insert(make_pair(Cross_c, Shape_c));
	category_recodings.insert(make_pair(Line_c, Shape_c));
	category_recodings.insert(make_pair(Bar_c, Shape_c));
	category_recodings.insert(make_pair(Heart_c, Shape_c));


} 

void Auditory_perceptual_processor::make_sound_stop(const Symbol& sound_name)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "make sound " << sound_name << " stop" << endl;

	// transmit the event forward to the next store
	schedule_event(new Auditory_Sound_Stop_event(
		get_time() + disappearance_delay.get_value(), get_human_ptr()->get_auditory_perceptual_store_ptr(),
		sound_name));
	// create and send a transient property forward
	schedule_event(new Auditory_Sound_Set_Property_event(
		get_time() + disappearance_delay.get_value(), get_human_ptr()->get_auditory_perceptual_store_ptr(),
		sound_name, Detection_c, Offset_c));
	// arrange to remove the transient after its delay
	schedule_event(new Auditory_Sound_Set_Property_event(
		get_time() + disappearance_delay.get_value() + transient_decay_time.get_value(), get_human_ptr()->get_auditory_perceptual_store_ptr(),
		sound_name, Detection_c, Nil_c));

}



// basic assumption: non-core properties are sent after a recoding time that is the intrinsic duration of the sound plus a recoding time
// not clear if this is sensible if a property changes well after the sound starts -- dk 4/19/10
Symbol Auditory_perceptual_processor::set_sound_property(const Symbol& object_name, const Symbol& property_name, const Symbol& property_value)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "set object " << object_name 
			<< " property " << property_name << " to " << property_value << endl;
			
	// get the object from the sensory store:
	Smart_Pointer<Auditory_sound> sound_ptr = get_human_ptr()->get_Auditory_sensory_store_ptr()->get_sound_ptr(object_name);
	long intrinsic_duration = sound_ptr->get_intrinsic_duration();

	// look up recoding time - no substantive recoding here - MUST FIX!
	Recoding_times_t::iterator it = recoding_times.find(property_name);
	if(it == recoding_times.end())
		throw Unknown_perceptual_property(this, property_name);
	long property_recoding_time = it->second;
	long recoding_time = long((property_recoding_time + intrinsic_duration) * recoding_time_fluctuation.get_double_value());
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << object_name 
			<< " property " << property_name << " recognized after " << intrinsic_duration << " + " <<  property_recoding_time 
			<< " for fluctuated total of " << recoding_time << endl;

	// transmit the event forward to the next store
	schedule_event(new Auditory_Sound_Set_Property_event(
		get_time() + recoding_time, get_human_ptr()->get_auditory_perceptual_store_ptr(),
		object_name, property_name, property_value));
	return property_value;
}
/*
	A delay event serves the purpose of allow a property to be transmitted after a time delay, 
	during which it can be cancelled by intervening events. A delay event contains
	the object, property, and values for a property-change event, 
	and the property-event-time at which the property is supposed to be delivered.
	If the delay event refers to a non-existent object, it is discarded.
	If the delay event arrives at a time that does not match the delivery time for the
	property that was stored with the object, it is discarded. Thus if the property event time
	has been set to zero, it means te delivery should be canceled. If the property event time
	mismatches and is larger, it means that a subsequent delivery has been scheduled, and this
	delivery should not be done.
	
	above copied, not edited, from original place in Visual_perceptual_processor
*/
void Auditory_perceptual_processor::handle_event(const Auditory_Delay_event * event_ptr)
{
	Symbol object_name = event_ptr->object_name;
	Symbol property_name = event_ptr->property_name;
	Symbol property_value = event_ptr->property_value;
	// check to see if the object is still present, do nothing if not
	if(!(get_human_ptr()->get_Auditory_sensory_store_ptr()->is_sound_present(object_name))) {
		if(get_trace() && Trace_out)
			Trace_out << processor_info() << object_name 
				<< " no longer present for delay event of " << property_value << " set to " << property_value << endl;
		return;
		}

	// if an encoder has been set, apply it and do nothing more if it wants to override the default behavior
	if(auditory_encoder_ptr && auditory_encoder_ptr->handle_Delay_event(object_name, property_name, property_value))
		return;

	// access the object
	Smart_Pointer<Auditory_sound> obj_ptr = get_sensory_object_ptr(object_name);
	// check to see if the object's event time for the property and the property value matches this event; if not, do nothing
//	long object_time = obj_ptr->get_property_event_time(property_name);
	Symbol object_property_value = obj_ptr->get_property_value(property_name);
/*	if(object_time != event_ptr->get_time() || object_property_value != property_value) {
		if(get_trace() && Trace_out)
			Trace_out << processor_info() << "Delay event discarded for " << object_name 
				<< " because event time and value " << event_ptr->get_time() << " " << property_value << " does not match stored " << object_time << " " << object_property_value << endl;
		return;
		}
*/
	// here if event matches - reset the stored event time, and transmit the information immediately to the perceptual store and 
	// transmit the event forward to the next store
//	obj_ptr->remove_property_event_time(property_name);
	schedule_event(new Auditory_Sound_Set_Property_event(
		get_time(), get_human_ptr()->get_auditory_perceptual_store_ptr(),
		object_name, property_name, property_value));
}

// This function seems to be required because my Smart_Pointer doesn't work properly
Smart_Pointer<Auditory_sound> Auditory_perceptual_processor::get_sensory_object_ptr(const Symbol& object_name)
{
	Auditory_sound * p = get_human_ptr()->get_Auditory_sensory_store_ptr()->get_sound_ptr(object_name);
	Smart_Pointer<Auditory_sound> obj_ptr = dynamic_cast<Auditory_sound *>(p);
	if(!obj_ptr)
		throw Epic_internal_error(this, "object was not an Auditory_sound");
	return obj_ptr;
}




