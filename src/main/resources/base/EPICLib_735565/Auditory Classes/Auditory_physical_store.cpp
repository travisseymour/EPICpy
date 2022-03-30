#include "Auditory_physical_store.h"
#include "../Framework classes/Speech_word.h"
#include "../Framework classes/Output_tee_globals.h"
#include "../Epic_standard_symbols.h"
#include "../Framework classes/Epic_exception.h"
//#include "Human_processor.h"
//#include "Human_subprocessor.h"
//#include "Auditory_store_processor.h"
#include "../Framework classes/Coordinator.h"
#include "Ear_processor.h"
#include "../Framework classes/Name_map.h"
#include "../Utility Classes/Symbol_utilities.h"
#include "../Model-View Classes/View_base.h"
//#include "Assert_throw.h"

#include <iostream>
//#include <string>
#include <sstream>
//#include <list>
#include <typeinfo>


using std::cout;	using std::endl;
using std::string;
using std::ostringstream;
//using std::list;



/*** Auditory_physical_stream ***/
/* sound name functionality disabled 5/7/12
Auditory_physical_stream::Auditory_physical_stream(const Symbol& name, GU::Point location, GU::Size size) :
		Auditory_stream(name, location, size), sound_name_counter(0)
{
	// create the first name
	create_next_sound_name();
}

// create and save the next sound's name, and return it 
// the name is streamname + sound_name_counter
Symbol Auditory_physical_stream::create_next_sound_name()
{
	next_sound_name = concatenate_to_Symbol("Snd", name, ++sound_name_counter);
	return next_sound_name;
}
*/


/*** Auditory_physical_store ***/

void Auditory_physical_store::initialize()
{
	Auditory_store::initialize();
//	psychological_names.clear();
//	physical_names.clear();
	name_map.clear();
	// seed name_map with some default names
	name_map.add_names(Default_physical_stream_c, Default_psychological_stream_c);
	stream_counter = 0;
	speech_item_counter = 0;
	
//	set_randomize_when_used(true);
//	set_randomize(true);
//	randomize();
//	describe_parameters(Normal_out);
}

void Auditory_physical_store::accept_event(const Auditory_event * event_ptr)
{
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << typeid(*event_ptr).name() << " received" << endl;
	broadcast_to_recorders(event_ptr);
	// tell the event to handle itself with itself!
	event_ptr->handle_self(this);
}

/* Stream inputs */

// this is the override for physical store - new object from device has only physical name
// generate the psychological object name, and then pass it on (flag added 1/25/2012)
void Auditory_physical_store::create_stream(const Symbol& physical_name, GU::Point location, GU::Size size, bool propagate_new_stream)
{	
/* disabled 5/7/12
	// create the new object
	insert_new(Auditory_physical_stream::create(physical_name, location, size));
	
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "create stream " << physical_name << " at " << location << endl;
			
	notify_views(&View_base::notify_auditory_stream_appear, physical_name, location, size);
	
	changed = true;
	
	// assign it an internal name, but special case the external and internal stream names
	Symbol psychological_name = (physical_name == External_c || physical_name == Overt_c || physical_name == Covert_c ) ? 
		physical_name : concatenate_to_Symbol("Strm_", physical_name, ++stream_counter);

	// add it to the name maps
	name_map.add_names(physical_name, psychological_name);
	
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "create stream " << physical_name << "/" << psychological_name << endl;

	// inform the next processor using psychological name only
	// but only if we want to propagate it 1/25/2012
	
	if(propagate_new_stream)
		get_human_ptr()->get_Ear_processor_ptr()->create_stream(psychological_name, location, size);
*/
}


// these functions use the base class then pass the call on if a change was made and needs testing
void Auditory_physical_store::destroy_stream(const Symbol& physical_name)
{
/* disabled 5/7/12
	// do the common processing on objects that are disappearing
	Auditory_store::destroy_stream(physical_name);
	// inform the next processor
	Symbol psychological_name = name_map.get_psychological_name(physical_name);
	get_human_ptr()->get_Ear_processor_ptr()->destroy_stream(psychological_name);
	// now that next processor has had a chance to see it, remove the object
	Auditory_store::erase_stream(physical_name);
	// remove the names
	name_map.remove_names_with_physical_name(physical_name);	// might have to wait for perceptual store to do this
*/
}

GU::Point Auditory_physical_store::set_stream_location(const Symbol& physical_name, GU::Point location)
{
/* disabled 5/7/12
	GU::Point old_value = Auditory_store::set_stream_location(physical_name, location);
	if(changed) {
		// inform the next processor
		const Symbol& psychological_name = name_map.get_psychological_name(physical_name);
		get_human_ptr()->get_Ear_processor_ptr()->set_stream_location(psychological_name, location);
		}
	return old_value;
*/
	return GU::Point();
}

GU::Size Auditory_physical_store::set_stream_size(const Symbol& physical_name, GU::Size size)
{
/* disabled 5/7/12
	GU::Size old_value = Auditory_store::set_stream_size(physical_name, size);
	if(changed) {
		// inform the next processor
		const Symbol& psychological_name = name_map.get_psychological_name(physical_name);
		get_human_ptr()->get_Ear_processor_ptr()->set_stream_size(psychological_name, size);
		}
	return old_value;
*/
	return GU::Size();
}


Symbol Auditory_physical_store::set_stream_property(const Symbol& physical_name, const Symbol& propname, const Symbol& propvalue)
{
/* disabled 5/7/12
	Symbol old_value = Auditory_store::set_stream_property(physical_name, propname, propvalue);
	if(changed) {
		// inform the next processor
		const Symbol& psychological_name = name_map.get_psychological_name(physical_name);
		get_human_ptr()->get_Ear_processor_ptr()->set_stream_property(psychological_name, propname, propvalue);
		}
	return old_value;
*/
	return Symbol();
}


void Auditory_physical_store::handle_event(const Auditory_Sound_Stop_event * event_ptr)
{
	Auditory_physical_store::make_sound_stop(event_ptr->sound_name);
}



/* Sound input functions */


// this is the override for physical store - new object from device has only physical name
// generate the psychological object name, and then pass it on with a next-link based on the stream name
void Auditory_physical_store::make_sound_start(const Symbol& physical_name, const Symbol& stream_name, GU::Point location,
			const Symbol& timbre, double loudness, long intrinsic_duration)
{
	// if the stream is unspecified, use the default name
	Symbol stream_physical_name = (stream_name != Symbol()) ? stream_name : Default_physical_stream_c;
	
	/* disabled 5/7/12
	// create a stream object if it is not already present
	if(!is_stream_present(stream_physical_name)) 
		create_stream(stream_physical_name, GU::Point());

	// get the (possibly default) psychological name of the stream
	const Symbol& stream_psychological_name = name_map.get_psychological_name(stream_name);
*/
	// backwards compatibility kludge 5/7/12
	Symbol stream_psychological_name = (stream_name != Symbol()) ? stream_name : Default_physical_stream_c;


	// create the new sound object - a continuing sound has duration 0
	long time_stamp = Coordinator::get_time();
	insert_new(Auditory_sound::create(physical_name, stream_psychological_name, time_stamp, location, timbre, loudness, 0, intrinsic_duration));

	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "start sound " << physical_name << ' '
		<< stream_physical_name << ' ' << timbre << ' '  << intrinsic_duration << endl;		

	notify_views(&View_base::notify_auditory_sound_start, physical_name, stream_physical_name, time_stamp, location, timbre, loudness);
	
	changed = true;
	/* disabled 5/7/12
	// now get the next name from the stream
	Symbol psychological_name = get_stream_ptr(stream_physical_name)->get_next_sound_name();
	// create the next name to use as the link for this sound to the next
	Symbol next_link = get_stream_ptr(stream_physical_name)->create_next_sound_name();  // needed to increment the counter
	
	// add it to the name maps
	name_map.add_names(physical_name, psychological_name);
	*/
	
	Symbol psychological_name = create_sound_name(physical_name);


	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "start sound " << physical_name << '/' << psychological_name << endl;		
	
	// inform the next processor in terms of psychological name only
	get_human_ptr()->get_Ear_processor_ptr()->make_new_sound_start(psychological_name, stream_psychological_name, time_stamp, location, timbre, loudness, intrinsic_duration);			
}


//void Auditory_physical_store::make_speech_start(const Symbol& physical_name, const Symbol& stream_name,  
//	const Symbol& content, const Symbol& speaker_gender, const Symbol& speaker_id, double loudness, long duration)
void Auditory_physical_store::make_speech_start(const Speech_word& physical_word)
{
	/* 1/25/2012 - although the "real" stream object won't be created until the words are processed, the stream name here is used
	as a basis for generating sound names - so this code has to remain */
	// if the stream is unspecified, use the default name
//	Symbol stream_physical_name = (physical_word.stream_name != Symbol()) ? physical_word.stream_name : Default_physical_stream_c;
	
	/* turn this off - streams created only perceptually - 5/7/12
	// create a stream object if it is not already present, but do not propagate it
	if(!is_stream_present(stream_physical_name)) 
		create_stream(stream_physical_name, GU::Point(), false);


	// get the (possibly default) psychological name of the stream
	const Symbol& stream_psychological_name = name_map.get_psychological_name(stream_physical_name);
	*/
		
	// copy the data, then change to psychological values
	Speech_word psychological_word = physical_word;
//	psychological_word.stream_name = stream_psychological_name; // 5/7/12

	// create the new sound object - a continuing sound has duration 0; use duration of speech unit as the intrinsic_duration odf the sound
	long time_stamp = Coordinator::get_time();
	psychological_word.time_stamp = time_stamp;
	psychological_word.name = create_sound_name(physical_word.name);
//	insert_new(Auditory_sound::create(physical_word.word_name, stream_psychological_name, time_stamp, Speech_c, physical_word.content, physical_word.speaker_gender, 
//		physical_word.speaker_id, physical_word.loudness, physical_word.pitch, 0, duration));
	insert_new(Auditory_sound::create(physical_word));

	if(get_trace() && Trace_out)
//		Trace_out << processor_info() << "start speech sound: " << physical_word.name << ' ' << stream_physical_name << ' '  
		Trace_out << processor_info() << "start speech sound: " << physical_word.name << ' ' << physical_word.stream_name << ' '  
		<< physical_word.content << ' ' << physical_word.speaker_gender << ' ' << physical_word.speaker_id << ' ' 
		<< physical_word.pitch << ' ' << physical_word.loudness << ' ' << physical_word.duration << endl;		
// ???TOFIX: this posts the physical word contents, but it does not have a valid time stamp
/*	notify_views(&View_base::notify_auditory_speech_start, physical_word.name, stream_physical_name, time_stamp, physical_word.content, 
		physical_word.speaker_gender, physical_word.speaker_id, physical_word.loudness, physical_word.pitch); */
	notify_views(&View_base::notify_auditory_speech_start, physical_word);
	
	changed = true;

/* no longer using this 5/7/12	
	// now get the next name from the stream
	Symbol psychological_name = get_stream_ptr(stream_physical_name)->get_next_sound_name();
	// create the next name to use as the link for this sound to the next
	// must fix below!
	Symbol next_link = get_stream_ptr(stream_physical_name)->create_next_sound_name();  //required to increment the sound counter!
	// change the time_stamp to be the start time stamp!
//	long end_time_stamp = start_time_stamp + duration;


	// add it to the name maps
	name_map.add_names(physical_word.name, psychological_word.name);

	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "propagate speech sound " << physical_word.name << '/' << psychological_word.name << endl;		
*/

	// inform the next processor in terms of psychological name only
	// change the time_stamp to be the start time stamp!
//	get_human_ptr()->get_Ear_processor_ptr()->make_new_speech_start(psychological_name, stream_psychological_name, time_stamp, content, speaker_gender, speaker_id, loudness, duration);			
	get_human_ptr()->get_Ear_processor_ptr()->make_new_speech_start(psychological_word);			
//	set_sound_property(physical_name, Start_time_c, start_time_stamp);
//	set_sound_property(physical_name, End_time_c, end_time_stamp);
}

Symbol Auditory_physical_store::create_sound_name(const Symbol& physical_name)
{
	Symbol psychological_name = concatenate_to_Symbol("Snd", physical_name, "_", ++speech_item_counter);
	name_map.add_names(physical_name, psychological_name);
	return psychological_name;
}	

// this is the override for physical store - let the next processor know the sound is gone,
// then remove it
void Auditory_physical_store::make_sound_stop(const Symbol& physical_name)
{
	// call the base function to note the sound is stopping
	Auditory_store::make_sound_stop(physical_name);

	// inform the next processor using the psychological name
	const Symbol& psychological_name = name_map.get_psychological_name(physical_name);

	if(get_trace() && Trace_out)
		Trace_out << processor_info() << "stop sound " << physical_name << '/' << psychological_name << endl;		

	get_human_ptr()->get_Ear_processor_ptr()->make_sound_stop(psychological_name);

	// now that next processor has had a chance to see it, remove the object
	erase_sound(physical_name);

}

// have the base class remove the objects, then remove the names
void Auditory_physical_store::erase_sound(const Symbol& physical_name)
{
	Auditory_store::erase_sound(physical_name);
//	name_map.remove_names_with_physical_name(physical_name); // let perceptual store delete the names
}


// This enables the device to "fire and forget" a sound that lasts a specific amount of time
// Create a sound object, but then schedule its removal at duration time from now.
void Auditory_physical_store::make_sound_event(const Symbol& physical_name, const Symbol& stream_name, GU::Point location,
			const Symbol& timbre, double loudness, long duration, long intrinsic_duration)
{
	// start the sound
	make_sound_start(physical_name, stream_name, location, timbre, loudness, intrinsic_duration);

	// make the sound stop at the end ofthe speech input
	schedule_event(new Auditory_Sound_Stop_event(get_time() + duration, this, physical_name));

}


// handle a speech event originated by Vocal_processor
void Auditory_physical_store::handle_event(const Auditory_Speech_event * event_ptr)
{
	// do the direct call to the function that does the work for externally-generated speech events
	// construct a Speech_word object from the event data
/*	Speech_word word;
	word.word_name = event_ptr->name;
	word.stream_name = event_ptr->stream_name;
	word.content = event_ptr->content;
	word.speaker_gender = event_ptr->speaker_gender;
	word.speaker_id = event_ptr->speaker_id;
	word.loudness = event_ptr->loudness;
	word.pitch = event_ptr->pitch;
	word.duration = event_ptr->duration;
*/	
//	make_speech_event(event_ptr->sound_name, event_ptr->stream_name, event_ptr->content,event_ptr->speaker_gender, event_ptr->speaker_id, event_ptr->loudness, event_ptr->duration);
	make_speech_event(event_ptr->word);
}


// This function allows other components to "fire & forget" long-duration speech input
// create an auditory object to represent the speech content,and schedule an event to remove it
// from the physical space at the end of the duration. The speech is reformulated as a sound
// with Timbre: Speech and Content:<utterance>.
//void Auditory_physical_store::make_speech_event(const Symbol& physical_name, const Symbol& stream_name, 
//		const Symbol& content, const Symbol& speaker_gender, const Symbol& speaker_id, double loudness, long duration)
void Auditory_physical_store::make_speech_event(const Speech_word& word)
{
	// the sound name here is the physical name
	make_speech_start(word);
	// timbre is Speech, the utterance becomes a Content property, intrinsic_duration is duration
//	make_speech_start(physical_name, stream_name, content, speaker_gender, speaker_id, loudness, duration);
//	set_sound_property(physical_name, Content_c, content);
//	set_sound_property(physical_name, Gender_c, speaker_gender);
//	set_sound_property(physical_name, Speaker_c, speaker_id);
	const Symbol& physical_name = word.name;
	
	if(get_trace() && Trace_out)
		Trace_out << processor_info() << " speech event started " << physical_name << '/' 
		<< name_map.get_psychological_name(physical_name) << endl;		
	
	// make the sound stop at the end of the speech input
	schedule_event(new Auditory_Sound_Stop_event(get_time() + word.duration, this, physical_name));

}


Symbol Auditory_physical_store::set_sound_property(const Symbol& physical_name, const Symbol& propname, const Symbol& propvalue)
{
	Symbol old_value = Auditory_store::set_sound_property(physical_name, propname, propvalue);
	if(changed) {
		// inform the next processor using the psychological name
		const Symbol& psychological_name = name_map.get_psychological_name(physical_name);
		get_human_ptr()->get_Ear_processor_ptr()->set_sound_property(psychological_name, propname, propvalue);
		}
	return old_value;
}
