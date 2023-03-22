#include "Ear_processor.h"
#include "../Framework classes/Epic_exception.h"
#include "../Framework classes/Output_tee_globals.h"

#include "Auditory_physical_store.h"
#include "Auditory_sensory_store.h"
#include "Stream_base.h"
#include "Stream_tracker_base.h"
#include "Stream_tracker_MinDistNoisy.h"
#include "Stream_tracker_MinDist.h"
#include "Stream_tracker_ClosestFirst.h"
#include "Auditory_event_types.h"
#include "Auditory_localization.h"
#include "../Utility Classes/Symbol_utilities.h"
#include "../Model-View Classes/View_base.h"
#include "../Utility Classes/Numeric_utilities.h"
#include "../Utility Classes/Random_utilities.h"
#include "../Standard_Symbols.h"

#include <string>
#include <list>
#include <iostream>
#include <limits>
#include <algorithm>
//#include <functional>

using std::vector;
using std::string;
using std::list;
using std::endl;
using std::map;	using std::make_pair;
using std::numeric_limits;
using std::remove_copy;

//using std::for_each;
//using std::mem_fun; using std::bind2nd;

/*** Exception classes ***/
class Unknown_physical_property : public Epic_exception {
public:
Unknown_physical_property(Processor * proc_ptr, const Symbol& propname)
	{
		msg = proc_ptr->processor_info() + 
		"Unknown physical property received: " + propname.str();
	}
};



const int max_n_sounds_present = 4;

/*** Ear_processor ***/

void Ear_processor::setup()
{
//	Auditory_physical_store& physical_store = *(get_human_ptr()->get_Auditory_physical_store_ptr());

	add_parameter(appearance_window);
	add_parameter(appearance_delay);
	add_parameter(disappearance_window);
	add_parameter(disappearance_delay);
	add_parameter(location_delay);
	add_parameter(property_window);
	add_parameter(property_delay);	
	add_parameter(effective_snr_pitch_weight);
	add_parameter(pitch_difference_max);
	add_parameter(content_detection1_dist_mean);
	add_parameter(content_detection2_dist_mean);
	add_parameter(content_detection3_dist_mean);
	add_parameter(content_detection_dist_sd);
	add_parameter(stream_alpha);
	add_parameter(stream_lambda);
	add_parameter(stream_theta);
	initialize_recodings();
	
	// choose our stream tracker at this point
	stream_tracker_ptr = new Stream_tracker_MinDistNoisy("Averaging_stream");
//	stream_tracker_ptr = new Stream_tracker_MinDist("Averaging_stream");
//	stream_tracker_ptr = new Stream_tracker_MinDist("Two_point_linear_stream");
//	stream_tracker_ptr = new Stream_tracker_ClosestFirst("Averaging_stream");
//	stream_tracker_ptr = new Stream_tracker_ClosestFirst("Two_point_linear_stream");
	
	// set up the four stream holders, with arbitrary names
//	streams.push_back(Stream_holder("Stream1"));
//	streams.push_back(Stream_holder("Stream2"));
//	streams.push_back(Stream_holder("Stream3"));
//	streams.push_back(Stream_holder("Stream4"));

}

// set overall state
void Ear_processor::initialize()
{
	Human_subprocessor::initialize();
	stream_tracker_ptr->clear();
//	set_trace(true);
//	set_randomize_when_used(true);
//	set_randomize(true);
//	randomize();
//	describe_parameters(Normal_out);
}

Ear_processor::~Ear_processor()
{
    delete stream_tracker_ptr;
}

void Ear_processor::accept_event(const Stop_event *)
{
//	physical_space.display_contents(Normal_out);
}

void Ear_processor::accept_event(const Auditory_event * event_ptr)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << typeid(*event_ptr).name() << " received" << endl;
	broadcast_to_recorders(event_ptr);
	// tell the event to handle itself with itself!
	event_ptr->handle_self(this);
}

/* Stream functions */

// The call includes the psychological name of the object.

/* disable 5/9/12
void Ear_processor::create_stream(const Symbol& name, GU::Point location, GU::Size size)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "create stream " << name << " at " << location << endl;
	
	// transmit the event forward to the next store
	schedule_event(new Auditory_Stream_Create_event(
		get_time() + appearance_delay.get_value(), get_human_ptr()->get_auditory_sensory_store_ptr(),
		name, location_noise(location), size));
		
	// tell the oculomotor processor about the appearance of a new object
	// MUST BE IMPLEMENTED 
	// if reflex enabled and on, and Invol_ocular processor is free,
	// make a reflex saccade to the new object, allowing for time for appearance information to get processed
//	if(reflex_enabled && reflex_on && free_to_move()) {
//		involuntary_movement_in_progress = true;
//		Smart_Pointer<Motor_action> action_ptr = new Invol_ocular_Saccade_action(get_human_ptr(), psychological_name);
//		action_ptr->dispatch(get_time() + appearance_delay.get_value() + inform_invol_ocular_delay.get_value());
//		}

}
*/

/* 
These functions are used to create or modify stream objects that are "downstream" in Auditory_sensory_store.
They do not apply to streams created or maintained in the Ear Processor.
*/

void Ear_processor::create_stream(const Symbol& name, double pitch, double loudness, GU::Point location)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "create stream " << name << " with " << pitch << ' ' << loudness << endl;
	
	// transmit the event forward to the next store
	schedule_event(new Auditory_Stream_Create_event(
		get_time() + appearance_delay.get_value(), get_human_ptr()->get_auditory_sensory_store_ptr(),
		name, pitch, loudness, location));
		
//		}

}

void Ear_processor::destroy_stream(const Symbol& name)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "destroy stream " << name << endl;

	// transmit it forward 
	schedule_event(new Auditory_Stream_Destroy_event( 
		get_time() + disappearance_delay.get_value(), get_human_ptr()->get_auditory_sensory_store_ptr(), 
		name));
}

GU::Point Ear_processor::set_stream_location(const Symbol& name, GU::Point location)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "set stream " << name 
			<< " location to " << location << endl;
			
	// transmit it forward and update the properties
	schedule_event(new Auditory_Stream_Set_Location_event(
		get_time() + location_delay.get_value(), get_human_ptr()->get_auditory_sensory_store_ptr(),
		name, location));
	return location;
}

double Ear_processor::set_stream_pitch(const Symbol& name, double pitch)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "set stream " << name 
			<< " pitch to " << pitch << endl;
			
	// transmit it forward and update the properties
	schedule_event(new Auditory_Stream_Set_Pitch_event(
		get_time() + location_delay.get_value(), get_human_ptr()->get_auditory_sensory_store_ptr(),
		name, pitch));
	return pitch;
}

double Ear_processor::set_stream_loudness(const Symbol& name, double loudness)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "set stream " << name 
			<< " loudness to " << loudness << endl;
			
	// transmit it forward and update the properties
	schedule_event(new Auditory_Stream_Set_Loudness_event(
		get_time() + location_delay.get_value(), get_human_ptr()->get_auditory_sensory_store_ptr(),
		name, loudness));
	return loudness;
}

GU::Size Ear_processor::set_stream_size(const Symbol& name, GU::Size size)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "set stream " << name 
			<< " size to " << size << endl;
			
	// transmit it forward and update the properties
	schedule_event(new Auditory_Stream_Set_Size_event(
		get_time() + location_delay.get_value(), get_human_ptr()->get_auditory_sensory_store_ptr(),
		name, size));
	return size;
}

Symbol Ear_processor::set_stream_property(const Symbol& obj_name, const Symbol& prop_name, 
	const Symbol& prop_value)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "set object " << obj_name 
			<< " property " << prop_name << " to " << prop_value << endl;
		
	// go head and send the property forward
	long delay = property_delay.get_value();
	// queue a message to the sensory store
	schedule_event(new Auditory_Stream_Set_Property_event(get_time() + delay, 
		get_human_ptr()->get_auditory_sensory_store_ptr(), obj_name, prop_name, prop_value));
	return prop_value;
}

/*
GU::Point Ear_processor::location_noise(GU::Point location)
{
	// dummy
	return location;
}
*/

void Ear_processor::make_new_sound_start(const Symbol& sound_name, const Symbol& stream_name, long time_stamp, 
	GU::Point location, const Symbol& timbre, double loudness, long intrinsic_duration)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "start sound " << sound_name << endl;
	
	schedule_event(new Auditory_Sound_Start_event(
		get_time() + appearance_window.get_value(), this,
		sound_name, stream_name, time_stamp, location, timbre, loudness, intrinsic_duration));

/*	// transmit the event forward to the next store
	schedule_event(new Auditory_Sound_Start_event(
		get_time() + appearance_delay.get_value(), get_human_ptr()->get_auditory_sensory_store_ptr(),
		name, stream, timbre, loudness, time_stamp, intrinsic_duration));
*/		
	// tell the oculomotor processor about the appearance of a new object
	// MUST BE IMPLEMENTED 
	// if reflex enabled and on, and Invol_ocular processor is free,
	// make a reflex saccade to the new object, allowing for time for appearance information to get processed
//	if(reflex_enabled && reflex_on && free_to_move()) {
//		involuntary_movement_in_progress = true;
//		Smart_Pointer<Motor_action> action_ptr = new Invol_ocular_Saccade_action(get_human_ptr(), psychological_name);
//		action_ptr->dispatch(get_time() + appearance_delay.get_value() + inform_invol_ocular_delay.get_value());
//		}

}

//void Ear_processor::make_new_speech_start(const Symbol& sound_name, const Symbol& stream_name, long time_stamp, 
//	const Symbol& content, const Symbol& speaker_gender, const Symbol& speaker_id, double loudness, long duration)
void Ear_processor::make_new_speech_start(const Speech_word& word)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "start speech " << word.name << endl;
	
	// create an event to come back to us at the end of the appearance_window time.
/*	schedule_event(new Auditory_Speech_Start_event(
		get_time() + appearance_window.get_value(), this,
		sound_name, stream_name, time_stamp, content, speaker_gender, speaker_id, loudness, duration)); */
	schedule_event(new Auditory_Speech_Start_event(
		get_time() + appearance_window.get_value(), this,
		word));

/*	// transmit the event forward to the next store
	schedule_event(new Auditory_Sound_Start_event(
		get_time() + appearance_delay.get_value(), get_human_ptr()->get_auditory_sensory_store_ptr(),
		name, stream, timbre, loudness, time_stamp, intrinsic_duration));
*/		
	// tell the oculomotor processor about the appearance of a new object
	// MUST BE IMPLEMENTED 
	// if reflex enabled and on, and Invol_ocular processor is free,
	// make a reflex saccade to the new object, allowing for time for appearance information to get processed
//	if(reflex_enabled && reflex_on && free_to_move()) {
//		involuntary_movement_in_progress = true;
//		Smart_Pointer<Motor_action> action_ptr = new Invol_ocular_Saccade_action(get_human_ptr(), psychological_name);
//		action_ptr->dispatch(get_time() + appearance_delay.get_value() + inform_invol_ocular_delay.get_value());
//		}

}

// here after the time window delay
void  Ear_processor::handle_event(const Auditory_Sound_Start_event * event_ptr)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "handle start sound event " << event_ptr->sound_name << endl;
		
	make_new_sound_start_f(event_ptr->sound_name, event_ptr->stream_name, event_ptr->time_stamp, event_ptr->location,
		event_ptr->timbre, event_ptr->loudness, event_ptr->intrinsic_duration);
}

/* void  Ear_processor::handle_event(const Auditory_Speech_Start_event * event_ptr)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "handle start speech event " << event_ptr->sound_name << endl;
		
	make_new_speech_start_f(event_ptr->sound_name, event_ptr->stream_name, event_ptr->time_stamp, 
		event_ptr->content, event_ptr->speaker_gender, event_ptr->speaker_id, 
		event_ptr->loudness, event_ptr->duration);
} */

void  Ear_processor::handle_event(const Auditory_Speech_Start_event * event_ptr)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "handle start speech event " << event_ptr->word.name << endl;
		
	make_new_speech_start_f(event_ptr->word);
}


const Symbol Acoustic_status_c("Acoustic_status");
const Symbol Masked_c("Masked");
const Symbol Content_masked_c("Content_masked");


void Ear_processor::make_new_sound_start_f(const Symbol& psychological_name, const Symbol& stream_name, long time_stamp,
    GU::Point original_location, const Symbol& timbre, double loudness, long intrinsic_duration)
{
	if(get_trace() && Trace_out) {
		Auditory_physical_store * physical_ptr = get_human_ptr()->get_Auditory_physical_store_ptr();
		Symbol_list_t sounds_present = physical_ptr->get_sound_name_list();
		Trace_out << "sounds now present: " << sounds_present << endl;
		}
    
    // apply the localization error function
    GU::Point location = apply_auditory_location_error(original_location);
	
/*	// flip a coin to decide whether to send the sound forward
	double x = unit_uniform_random_variable();
	double threshold = simple_content_masking_probability.get_double_value();
	if(x < threshold) {
		if(get_trace() && Trace_out)
			Trace_out << processor_info() << "sound " << psychological_name << " is masked" << endl;
		// mark the sound as masked
		Auditory_physical_store * physical_ptr = get_human_ptr()->get_Auditory_physical_store_ptr();
		const Symbol& physical_name = physical_ptr->get_name_map().get_physical_name(psychological_name);
		Smart_Pointer<Auditory_sound> sound_ptr = physical_ptr->get_sound_ptr(physical_name);
		sound_ptr->set_property(Acoustic_status_c, Content_masked_c);
		return; // don't send forward
		}

	// the sound is not masked; flip a coin to see if the stream name will be passed forward
	x = unit_uniform_random_variable();
	threshold = simple_stream_masking_probability.get_double_value();
	Symbol stream_id = stream;
	if(x < threshold) {
		if(get_trace() && Trace_out)
			Trace_out << processor_info() << "sound " << psychological_name << " stream id " << stream << " is masked" << endl;
		stream_id = Symbol();
		}
*/
	/* flip independent coins to decide whether to mask content and/or stream ID - dk 5/25/10 */

/// no masking of sounds at this time dk 8/2/2010

/*
	double x = unit_uniform_random_variable();
	double threshold = simple_content_recognition_probability.get_double_value();
	if(x < threshold) {
		if(get_trace() && Trace_out)
			Trace_out << processor_info() << "sound " << psychological_name << " content is masked" << endl;
		// mark the sound as masked
		Auditory_physical_store * physical_ptr = get_human_ptr()->get_Auditory_physical_store_ptr();
		const Symbol& physical_name = physical_ptr->get_name_map().get_physical_name(psychological_name);
		Smart_Pointer<Auditory_sound> sound_ptr = physical_ptr->get_sound_ptr(physical_name);
		sound_ptr->set_property(Acoustic_status_c, Content_masked_c);
		}

	x = unit_uniform_random_variable();
	threshold = simple_stream_recognition_probability.get_double_value();
	Symbol stream_id = stream_name;
	if(x < threshold) {
		if(get_trace() && Trace_out)
			Trace_out << processor_info() << "sound " << psychological_name << " stream id " << stream_name << " is masked" << endl;
		stream_id = Symbol();
		}
*/	
	
	// transmit the event forward to the next store
	schedule_event(new Auditory_Sound_Start_event(
		get_time() + appearance_delay.get_value(), get_human_ptr()->get_auditory_sensory_store_ptr(),
		psychological_name, stream_name, time_stamp, location, timbre, loudness, intrinsic_duration));
		
	// tell the oculomotor processor about the appearance of a new object
	// MUST BE IMPLEMENTED 
	// if reflex enabled and on, and Invol_ocular processor is free,
	// make a reflex saccade to the new object, allowing for time for appearance information to get processed
//	if(reflex_enabled && reflex_on && free_to_move()) {
//		involuntary_movement_in_progress = true;
//		Smart_Pointer<Motor_action> action_ptr = new Invol_ocular_Saccade_action(get_human_ptr(), psychological_name);
//		action_ptr->dispatch(get_time() + appearance_delay.get_value() + inform_invol_ocular_delay.get_value());
//		}

}

const Symbol Self_c("Self");
const Symbol Callsign_c("Callsign");
const Symbol Digit_c("Digit");
const Symbol Stream_assignment_c("Stream_assignment");

class Access_physical_name {
public:
	Access_physical_name (Auditory_physical_store * ptr_) : physical_store_ptr(ptr_) {}
	Symbol operator() (const Symbol& psychological_name) const
		{return physical_store_ptr->get_name_map().get_physical_name(psychological_name);}
private:
	Auditory_physical_store * physical_store_ptr;
};

/* 
make_new_speech_start_f 
--- as of 2/2012
Implemented "stream tracker" in which each word is assigned to a stream object based on loudness and pitch,
and then the stream object is updated with the loudness and pitch of its assigned word.

--- 1/16/2012
For sanity, earlier code that was commented out has been removed. See previous versions if needed.

This version adopts a much simpler preliminary masking model. The speaker-gender, and speaker-id field are neither
processed nor passed along. Instead loudness and pitch are used by the cognitive processor to associate words to streams.

As of 1/16/2012 the following rules implemented:

1. loudness and pitch will vary at the source (the device) stochastically according to speaker/gender.
2. loudness and pitch are always passed through - no masking at this time.
3. content is probability masked using a function of SNR only at this time

Assume we have two streams, stream1 and stream2.
--- as of 4/27/2012
attempt to scale up to four streams, stream1, stream2, stream3, stream4

*/

void Ear_processor::make_new_speech_start_f(const Speech_word& word)
{
	Auditory_physical_store * physical_store_ptr = get_human_ptr()->get_Auditory_physical_store_ptr();
	Symbol_list_t sounds_present = physical_store_ptr->get_sound_name_list();

	if(get_trace() && Trace_out) {
		Trace_out << "sounds now present: " << sounds_present << endl;
		}
    // make a copy of the speech word to be propagated
    Speech_word word_propagated = word;

    // *** *** *** NOTE NOTE NOTE - location error is in the propagated word, not the original word here !
    // if any stream tracking uses location, this needs to be reconsidered!
    
    // apply auditory localization error function
    word_propagated.location = apply_auditory_location_error(word.location);
    
	// defaults for pass-through
	Symbol content_propagated = word.content;
	Symbol stream_propagated = word.stream_name;
    


// Below as of 7/8/14 is good fit to Rep 2 with V7aUse
/*
// From Greg 060714 xxxJun02RepAll_UWYH_Trk43ab_Fitv23ab
    const double callsign_means[3] = {-21, -22, -19};
    const double callsign_sds[3] = {6, 15, 15};
    const double color_means[3] = {-24, -25, -20};
    const double color_sds[3] = {6, 12, 13};
    const double digit_means[3] = {-30, -25, -25,};
    const double digit_sds[3] = {4, 6, 6};
	const double lambdas[3] = {0.6, 0.6, 0.65};
	const double alphas[3] = {0.05, .02, .02};
	const double thetas[3] = {0.45, 0.45, 0.55};
*/
// modified From Greg 060714 xxxJun02RepAll_UWYH_Trk43ab_Fitv23ab
/*
	const double effective_snr_pitch_difference_weight = 3.0;
	const double pitch_difference_cap = 4.0;
	const double callsign_means[3] = {-15, -15, -15};
	const double callsign_sds[3] = {10, 10, 10};
	const double color_means[3] = {-17, -17, -17};
	const double color_sds[3] = {10, 10, 10};
//	const double digit_means[3] = {-24, -24, -24,}; // note typo here
	const double digit_means[3] = {-24, -24, -24};
    const double digit_sds[3] = {10, 10, 10};
	const double lambdas[3] = {.65, .65, .65};
	const double alphas[3] = {0.02, 0.02, 0.02};
	const double thetas[3] = {0.55, 0.55, 0.55};
*/

// modified From Greg 060714 xxxJun02RepAll_UWYH_Trk43ab_Fitv23ab
	const double effective_snr_pitch_difference_weight = effective_snr_pitch_weight.get_double_value();
	const double pitch_difference_cap = pitch_difference_max.get_double_value();
	double sd = content_detection_dist_sd.get_double_value();
	double m1 = content_detection1_dist_mean.get_double_value();
	double m2 = content_detection2_dist_mean.get_double_value();
	double m3 = content_detection3_dist_mean.get_double_value();
	const double callsign_means[3] = {m1, m1, m1};
	const double callsign_sds[3] = {sd, sd, sd};
	const double color_means[3] = {m2, m2, m2};
	const double color_sds[3] = {sd, sd, sd};
	const double digit_means[3] = {m3, m3, m3};
	const double digit_sds[3] = {sd, sd, sd};
	double alpha = stream_alpha.get_double_value();
	const double alphas[3] = {alpha, alpha, alpha};
	double lambda = stream_lambda.get_double_value();
	const double lambdas[3] = {lambda, lambda, lambda};
	double theta = stream_theta.get_double_value();
	const double thetas[3] = {theta, theta, theta};
//    Normal_out << "Parameter values " << effective_snr_pitch_difference_weight << ' ' << pitch_difference_cap
//        << ' ' << m1 << ' ' << m2 << ' ' << m3 << ' ' << sd << ' ' << alpha << ' ' << lambda << ' ' << theta << endl;


/*
// From Greg 061813 PM
    const double callsign_means[3] = {-21, -20, -18}; // original
//    const double callsign_means[3] = {-12, -13, -9}; // modified
    const double callsign_sds[3] = {10, 10, 10}; // original
//    const double callsign_sds[3] = {12, 12, 12}; //modified
    const double color_means[3] = {-26, -24, -20}; // original
//    const double color_means[3] = {-23, -21, -17}; // modified
    const double color_sds[3] = {10, 10, 10};
    const double digit_means[3] = {-31, -28, -26,}; // original
//    const double digit_means[3] = {-28, -28, -23,}; // modified
    const double digit_sds[3] = {10, 10, 10};
	const double lambdas[3] = {0.75, 0.75, 0.75};
	const double thetas[3] = {0.35, 0.35, 0.35};
	const double alphas[3] = {0.04, 0.05, 0.05};
*/
/*
// modifications of 061813 to fit 3S, 4S data
    const double callsign_means[3] = {-3, -2, -6};
    const double callsign_sds[3] = {3, 3, 3};
    const double color_means[3] = {-8, -6, -2};
    const double color_sds[3] = {3, 3, 3};
    const double digit_means[3] = {-13, -10, -8,};
    const double digit_sds[3] = {3, 3, 3};
//	const double lambdas[3] = {0.75, 0.75, 0.75};
//	const double thetas[3] = {0.35, 0.35, 0.35};
//	const double alphas[3] = {0.04, 0.05, 0.05};
//effective snr pitch weight		0
*/
    
		
	// if more than one sound, apply masking mechanism
	// and stream tracking mechanism
	int n_sounds_present = int(sounds_present.size());
	if(n_sounds_present > 1) {
		Assert(n_sounds_present <= max_n_sounds_present);
		const Symbol& this_physical_name = physical_store_ptr->get_name_map().get_physical_name(word.name);
		Smart_Pointer<Auditory_sound> this_sound_ptr = physical_store_ptr->get_sound_ptr(this_physical_name);
		const Symbol& this_content = this_sound_ptr->get_content();
		double this_loudness = this_sound_ptr->get_loudness();
        // all the pitches are being supplied as semitones
		double this_pitch = this_sound_ptr->get_pitch();
        Symbol this_gender = this_sound_ptr->get_gender();
        Symbol this_speaker_id = this_sound_ptr->get_speaker_id();

		// get a list of the other sounds present - this is a list of their physical names
		Symbol_list_t other_sounds_present;
		remove_copy(sounds_present.begin(), sounds_present.end(), back_inserter(other_sounds_present), this_physical_name);
		Assert(other_sounds_present.size() <= n_sounds_present - 1);
		// calculate effective loudness snr based on other sounds present
		double total_masking_power = 0.;
        // depending on the conditions, these might not have a single value, but should be well defined compared to
        // the attribute for "this" sound.  
        Symbol other_gender;  // must be different from this sound for TD, same for TS and TT
        Symbol other_speaker_id; // must be different from this sound for TD and TS, but same for TT
		pitch_stats.reset();
		for(Symbol_list_t::iterator it = other_sounds_present.begin(); it != other_sounds_present.end(); ++it) {
			Smart_Pointer<Auditory_sound> other_sound = physical_store_ptr->get_sound_ptr(*it);
			total_masking_power += pow(10., other_sound->get_loudness() / 10.);
			// compute pitch statistics for other sounds, note that semitones are present
			pitch_stats.update(other_sound->get_pitch());
            other_gender = other_sound->get_gender();
            other_speaker_id = other_sound->get_speaker_id();
			}
		double total_masking_db = 10. * log10(total_masking_power);
		double loudness_snr = this_loudness - total_masking_db;
		double pitch_difference = fabs(this_pitch - pitch_stats.get_mean());

		// determine the condition we are in
		int condidx = -1;
		if(this_speaker_id == other_speaker_id)
			condidx = 2;    //TT
		else if(this_gender == other_gender)
			condidx = 1;    //TS
		else if(this_gender != other_gender)
			condidx = 0;    //TD
		else
			Assert(!"invalid condition configuration");
		Assert(condidx >= 0 && condidx <= 2);
		
		if(pitch_difference > pitch_difference_cap)
			pitch_difference = pitch_difference_cap;
		double snr = loudness_snr +  effective_snr_pitch_difference_weight * pitch_difference;

    
		if(get_trace() && Trace_out)
			Trace_out << processor_info() << "processing " << this_sound_ptr->get_name() << " db " 
				<< this_loudness << " masking " << total_masking_db << " " << loudness_snr << " "
				<< this_pitch << " compared to " << pitch_stats.get_mean() << " " << pitch_difference << " " << snr << endl;

		// Because we wait until all words have arrived, at this point they all have,
        // but we have to process them one at a time.
        // So we have to check on whether we have assigned words to the sreams yet. 
		// determine if all words are unassigned
        // this would be faster if we had a container of sound_ptrs instead.
		bool words_unassigned = true;
		for(Symbol_list_t::iterator it = sounds_present.begin(); it != sounds_present.end(); ++it) {
			Smart_Pointer<Auditory_sound> sound_ptr = physical_store_ptr->get_sound_ptr(*it);
			// all sounds must be unassigned for words_unassigned to end up as true
			words_unassigned = words_unassigned && (sound_ptr->get_property_value(Stream_assignment_c) == Nil_c);
			}
			       
		// We need to assign each word to one stream so that each stream has one word.
		// Veridical stream_ID in word is ignored
		if(words_unassigned) {
            // give the stream tracker the sounds
            stream_tracker_ptr->clear_sounds();
            for(Symbol_list_t::iterator it = sounds_present.begin(); it != sounds_present.end(); ++it)
                stream_tracker_ptr->add_sound(physical_store_ptr->get_sound_ptr(*it));
 
            // now ready to do stream assignment work - have we started the streams yet?
            // note that long delay will result in streams being deleted, so "resets" automatically
			if(!stream_tracker_ptr->are_streams_started()) {
				stream_tracker_ptr->create_initial_streams();
				// get streams after assignment
				const vector<std::shared_ptr<Stream_base>>& streams = stream_tracker_ptr->get_streams();
				// request creation of a stream object in the auditory store for each stream
				for(auto the_stream : streams) {
					create_stream(
						the_stream->get_name(),
						the_stream->get_predicted_pitch(),
						the_stream->get_predicted_loudness(),
						GU::Point() // default location is center
						);
					}

/*				// KULDGE SANITY CHECK - USE AND PASS FORWARD VERIDICAL STREAM NAMES
				this_sound_ptr->set_property(Stream_assignment_c, this_sound_ptr->get_stream());
				other_sound_ptr->set_property(Stream_assignment_c, other_sound_ptr->get_stream());
*/
				} // done with creating initial streams

			// do this only after the first word
//			else if (word.content != "ready") {
			else if (stream_tracker_ptr->are_streams_started()) { // assign sounds to existing streams
				// this work does not require distingishing "this_sound" from the other sounds
				// set parameters in the stream tracker
				stream_tracker_ptr->set_lambda(lambdas[condidx]);
				stream_tracker_ptr->set_theta(thetas[condidx]);
				stream_tracker_ptr->set_alpha(alphas[condidx]);
				
				stream_tracker_ptr->assign_sounds_to_streams();
				// get streams after assignment
				const vector<std::shared_ptr<Stream_base>>& streams = stream_tracker_ptr->get_streams();
				// update the stream object in the auditory store for each stream
				for(auto the_stream : streams) {
					set_stream_pitch(the_stream->get_name(), the_stream->get_predicted_pitch());
					set_stream_loudness(the_stream->get_name(), the_stream->get_predicted_loudness());
					}
							
				} // done with assigning sounds to existing streams
			} // done with stream assignment work

		// at this point the stream assignment/updating has been done for both this sound / word and the other sound present as well.
		// the stream id to be propagated for the current word has been saved with the sound
		// and is one of the arbitrary symbols in the form of "Stream1" etc.
		stream_propagated = this_sound_ptr->get_property_value(Stream_assignment_c);
		Assert(stream_propagated != Nil_c);
		
		// get the content category (kludge for model fitting)
		// Either Digit_c, Color_c, or Nil_c;
		Category_recodings_t::iterator category_it = category_recodings.find(this_content);
		Symbol this_category = (category_it != category_recodings.end()) ? category_it->second : Nil_c;

		bool content_detected = false;
		bool stream_detected = true; // stream attributes always passed through (loudness, pitch) along with stream_id
		
		// kluge for verbal WM models where one of the speakers is Self - covert rehearsal - no masking!
/*		if(this_sound_ptr->get_speaker_id() == Self_c || other_sound_ptr->get_speaker_id() == Self_c) {	
// Covert speech during input
			content_detected = true;
			speaker_detected = true;
			reloud_detected = true;
			stream_detected = true;
			}
*/

// content is passed through as a function of snr only
//	simple detection model
{
    Assert(condidx >= 0 && condidx <= 2);
   
    double detection_mean = 0, detection_sd = 1;
	if(this_category == Nil_c || this_category == Callsign_c) {
        detection_mean = callsign_means[condidx];
        detection_sd = callsign_sds[condidx];
        }
	else if(this_category == Color_c) {
        detection_mean = color_means[condidx];
        detection_sd = color_sds[condidx];
        }
	else if(this_category == Digit_c) {
        detection_mean = digit_means[condidx];
        detection_sd = digit_sds[condidx];
        }
    else {
		Assert(!"Invalid category!");
		}
    
//    Normal_out << "Dectection " << this_category << ' ' << condidx << ' ' << detection_mean << ' ' << detection_sd << endl;
    
    content_detected = ogive_detection_function(snr, detection_mean, detection_sd);
	/*
    if(this_category == Color_c) {
        static double sum_neg = 0;
        static long n_neg = 0;
        static long count = 0;
        static long n = 0;
        static long n_above_mean = 0;
        if(snr < 0) {
            n_neg++;
            sum_neg += snr;
            if (snr > -18)
                n_above_mean++;
            }
        n++;
        if(content_detected)
            count++;
        Normal_out << "detecting color: " << snr << ' ' << detection_mean << ' ' << detection_sd << ' '<< double(count) / double(n) << ' ' << sum_neg / n_neg << ' ' << double(n_above_mean) / n_neg << endl;
        }
		*/
}
 
		// apply the content masking result
		content_propagated = (content_detected) ? word.content : Nil_c;
		if(!content_detected) {
			if(get_trace() && Trace_out)
				Trace_out << processor_info() << "speech sound " << word.name << " content " << word.content << " is masked" << endl;
			// mark this speech sound as masked
			this_sound_ptr->set_property(Acoustic_status_c, Content_masked_c);
			}
		
		// apply the stream masking result
		if(!stream_detected) {
			if(get_trace() && Trace_out)
				Trace_out << processor_info() << "speech sound " <<word.name << " stream id " << word.stream_name << " is masked" << endl;
			}
	
	}
	
	// populate the speech event to be propagated
	word_propagated.stream_name = stream_propagated; // loudness and pitch are also propagated always - 01162012
	word_propagated.content = content_propagated;
		
	schedule_event(new Auditory_Speech_Start_event(
		get_time() + appearance_delay.get_value(), get_human_ptr()->get_auditory_sensory_store_ptr(),
		word_propagated));

	// tell the oculomotor processor about the appearance of a new object
	// MUST BE IMPLEMENTED 
	// if reflex enabled and on, and Invol_ocular processor is free,
	// make a reflex saccade to the new object, allowing for time for appearance information to get processed
//	if(reflex_enabled && reflex_on && free_to_move()) {
//		involuntary_movement_in_progress = true;
//		Smart_Pointer<Motor_action> action_ptr = new Invol_ocular_Saccade_action(get_human_ptr(), psychological_name);
//		action_ptr->dispatch(get_time() + appearance_delay.get_value() + inform_invol_ocular_delay.get_value());
//		}

}

	
void Ear_processor::make_sound_stop(const Symbol& name)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "make sound stop " << name << endl;

// do not impose a time window on stop events but do check to see if we got masking before sending it on
	make_sound_stop_f(name);

/*
	schedule_event(new Auditory_Sound_Stop_event(
		get_time() + disappearance_window.get_value(), this,
		name));
*/
	// transmit it forward 
//	schedule_event(new Auditory_Sound_Stop_event( 
//		get_time() + disappearance_delay.get_value(), get_human_ptr()->get_auditory_sensory_store_ptr(), 
//		name));
}

// here after the time window delay
void  Ear_processor::handle_event(const Auditory_Sound_Stop_event * event_ptr)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "handle sound stop event " << event_ptr->sound_name << endl;
		
	make_sound_stop_f(event_ptr->sound_name);
}

void Ear_processor::make_sound_stop_f(const Symbol& psychological_name)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "make sound stop " << psychological_name << endl;
/* since we flipped independent coins to decide whether to mask content and/or stream ID, sound was always propagated,
so that it is stopped should be also always propagated - dk 5/25/10 */
/*
	// check to see if the sound is masked
	bool was_masked = false;
	Auditory_physical_store * physical_ptr = get_human_ptr()->get_Auditory_physical_store_ptr();
	// ifthe sound psychological_name is present, access the physical name and see if it was masked;
	// if it is not present, assume that this is not an error but that it is gone because of masking
	if(physical_ptr->get_name_map().is_psychological_name_present(psychological_name)) {
		const Symbol& physical_name = physical_ptr->get_name_map().get_physical_name(psychological_name);
		Smart_Pointer<Auditory_sound> sound_ptr = physical_ptr->get_sound_ptr(physical_name);
		was_masked = (sound_ptr->get_property_value(Acoustic_status_c) == Masked_c);
		}
	else
		was_masked = true;
		
	// if masked, do nothing
	if(was_masked) {
		if(get_trace() && Trace_out)
			Trace_out << processor_info() << "sound stop " << psychological_name 
				<< " suppressed due to masking" << endl;
		return;
		}
		
	// otherwise, transmit it forward 
*/
	schedule_event(new Auditory_Sound_Stop_event( 
		get_time() + disappearance_delay.get_value(), get_human_ptr()->get_auditory_sensory_store_ptr(), 
		psychological_name));
	
	// get the stream for this sound
	Auditory_physical_store * physical_store_ptr = get_human_ptr()->get_Auditory_physical_store_ptr();
	const Symbol& physical_name = physical_store_ptr->get_name_map().get_physical_name(psychological_name);
	Smart_Pointer<Auditory_sound> sound_ptr = physical_store_ptr->get_sound_ptr(physical_name);
	const Symbol& stream_name = sound_ptr->get_property_value(Stream_assignment_c);
	// if there is no stream associated with this sound, then quit
	if(stream_name == Nil_c)
		return;
	long disappearance_time = get_time() + disappearance_delay.get_value();
	stream_tracker_ptr->set_stream_disappearance_time(stream_name, disappearance_time);
	
	// schedule event to destroy our stream object in the future if not refreshed
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "destroy event for " << stream_name << " scheduled for " << disappearance_time << endl;
	schedule_event(new Auditory_Stream_Destroy_event(
		disappearance_time, this,
		stream_name));

}

void Ear_processor::handle_event(const Auditory_Stream_Destroy_event * event_ptr)
{
	// find the stream holder object with this name and get its disappearance time
	// if same as event time, then delete this stream object and send a stream destroy event downstream
	long event_time = event_ptr->get_time();
	Symbol stream_name = event_ptr->stream_name;
	// find the stream holder object with this name and disappearance time and get rid of it
    // need a copy of the stream container, because we modify the original in this process
    vector<std::shared_ptr<Stream_base>> streams = stream_tracker_ptr->get_streams();
    for(auto the_stream : streams) {
        if(the_stream->get_name() == stream_name && the_stream->get_disappearance_time() == event_time) {
            if(get_trace() && Trace_out)
                Trace_out << processor_info() << "stream holder" << the_stream->get_name() << " deleted & sensory stream scheduled to be destroyed" << endl;
            stream_tracker_ptr->delete_stream(stream_name);
            schedule_event(new Auditory_Stream_Destroy_event( 
                    get_time() + disappearance_delay.get_value(), get_human_ptr()->get_auditory_sensory_store_ptr(), 
                    stream_name));
            return;  // only one stream event supposed to be possible
			}
		}



	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "destroy event for " << stream_name << " discarded because " << event_time << " not matched" << endl;
}


// sound property changes are also window-delayed so that masking might happen
Symbol Ear_processor::set_sound_property(const Symbol& obj_name, const Symbol& prop_name, 
	const Symbol& prop_value)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "set sound " << obj_name 
			<< " property " << prop_name << " to " << prop_value << endl;

	schedule_event(new Auditory_Sound_Set_Property_event(
		get_time() + property_window.get_value(), this,
		obj_name, prop_name, prop_value));

/*		
	// go head and send the property forward
	long delay = property_delay.get_value();
	// queue a message to the sensory store
	schedule_event(new Auditory_Sound_Set_Property_event(get_time() + delay, 
		get_human_ptr()->get_auditory_sensory_store_ptr(), obj_name, prop_name, prop_value));
*/
	return prop_value;
}

// here after the time window delay
void  Ear_processor::handle_event(const Auditory_Sound_Set_Property_event * event_ptr)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "handle set property event " << event_ptr->sound_name << endl;
		
	set_sound_property_f(event_ptr->sound_name, event_ptr->property_name, event_ptr->property_value);
}

// this might not be needed

Symbol Ear_processor::set_sound_property_f(const Symbol& psychological_name, const Symbol& prop_name, 
	const Symbol& prop_value)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "set sound " << psychological_name 
			<< " property " << prop_name << " to " << prop_value << endl;
	// check to see if the sound is masked
	Auditory_physical_store * physical_ptr = get_human_ptr()->get_Auditory_physical_store_ptr();
	const Symbol& physical_name = physical_ptr->get_name_map().get_physical_name(psychological_name);
	Smart_Pointer<Auditory_sound> sound_ptr = physical_ptr->get_sound_ptr(physical_name);
	// if content is masked, do nothing - dk 5/22/10
	if(sound_ptr->get_property_value(Acoustic_status_c) == Content_masked_c) {
		if(get_trace() && Trace_out)
			Trace_out << processor_info() << "set sound " << psychological_name 
				<< " property " << prop_name << " to " << prop_value << " suppressed due to content masking" << endl;
		return prop_value;
		}
		
	// go head and send the property forward
	long delay = property_delay.get_value();
	// queue a message to the sensory store
	schedule_event(new Auditory_Sound_Set_Property_event(get_time() + delay, 
		get_human_ptr()->get_auditory_sensory_store_ptr(), psychological_name, prop_name, prop_value));
	return prop_value;
}


void Ear_processor::initialize_recodings()
{
	// classify content by look-up
//	category_recodings.insert(make_pair(Symbol("Baron"), Callsign_c));
	category_recodings.insert(make_pair(Symbol("arrow"),   Callsign_c));
	category_recodings.insert(make_pair(Symbol("baron"),   Callsign_c));
	category_recodings.insert(make_pair(Symbol("charlie"), Callsign_c));
	category_recodings.insert(make_pair(Symbol("eagle"),   Callsign_c));
	category_recodings.insert(make_pair(Symbol("hopper"),  Callsign_c));
	category_recodings.insert(make_pair(Symbol("laker"),   Callsign_c));
	category_recodings.insert(make_pair(Symbol("ringo"),   Callsign_c));
	category_recodings.insert(make_pair(Symbol("tiger"),   Callsign_c));

	category_recodings.insert(make_pair(Blue_c, Color_c));
	category_recodings.insert(make_pair(Green_c, Color_c));
	category_recodings.insert(make_pair(Red_c, Color_c));
	category_recodings.insert(make_pair(White_c, Color_c));
	
	category_recodings.insert(make_pair(Symbol(1), Digit_c));
	category_recodings.insert(make_pair(Symbol(2), Digit_c));
	category_recodings.insert(make_pair(Symbol(3), Digit_c));
	category_recodings.insert(make_pair(Symbol(4), Digit_c));
	category_recodings.insert(make_pair(Symbol(5), Digit_c));
	category_recodings.insert(make_pair(Symbol(6), Digit_c));
	category_recodings.insert(make_pair(Symbol(7), Digit_c));
	category_recodings.insert(make_pair(Symbol(8), Digit_c));
	category_recodings.insert(make_pair(Symbol(9), Digit_c));
} 

