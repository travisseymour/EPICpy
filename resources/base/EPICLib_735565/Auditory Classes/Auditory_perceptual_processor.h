/* The auditory perceptual processor accepts direct calls from the Auditory_sensory_store,
and emits events to the Auditory_perceptual_store. It does any recoding (currently none)
and creates some transient events sent downstream (which probably should be done by the ear
processor).

*/

#ifndef AUDITORY_PERCEPTUAL_PROCESSOR_H
#define AUDITORY_PERCEPTUAL_PROCESSOR_H

#include <map>
#include "../Utility Classes/Output_tee.h"
#include "../Framework classes/Human_subprocessor.h"
#include "Auditory_processor.h"
#include "Auditory_store.h"
#include "../Framework classes/Parameter.h"
/* 
Auditory_sensory_store does direct calls to this processor, which recodes the information
and sends scheduled event to Auditory_perceptual_store, with various delays as appropriate,
and also transient properties ???

At this time, all perceptual recoding is done here - the Auditory_perceptual_store
simply passes-through relevant information to the cognitive processor.
*/

#include "../Utility Classes/Geometry.h"
namespace GU = Geometry_Utilities;
//#include "Auditory_perceptual_processor_event_types.h"
//#include "Auditory_event_types.h"

class Human_processor;
class Symbol;
class Auditory_Delay_event;
class Auditory_encoder_base;

class Auditory_perceptual_processor : public Auditory_processor {
public:
	Auditory_perceptual_processor(Human_processor * human_ptr_) :
		Auditory_processor ("Auditory_perceptual_processor", human_ptr_),
		// delay for new streams and sounds to be passed on
		appearance_delay("Appearance_recoding_time", 50),
		// delay for cessation of streams and sounds to be passed on
		// this stretches out the effective duration of a stream or sound
		disappearance_delay("Disappearance_recoding_time", 50),
		// delay for passing on a change in stream location or size
		location_delay("Location_change_recoding_time", 50),
		recoded_location_delay("Recoded_location_delay", 100),
		// fluctuations for delay for passing on a change in a property
//		property_time_fluctuation("Property_delay_fluctuation_factor", Parameter::Normal, Parameter::Never, 1.0, .5),
		recoding_time_fluctuation("Recoding_time_fluctuation_factor", Parameter::Normal, Parameter::Never, 1.0, .5),
		recoding_failure_rate1("Recoding_failure_rate1", 0.5), // Custom failure rate #1

		// time that transient signals last - e.g. onsets, offsets, changes
		transient_decay_time("Transient_decay_time", 75),
        auditory_encoder_ptr(nullptr)
		{
			setup();
		}

	virtual void initialize();
	
	// set externally with an address supplied by a dynamic library - connects this processor back to it.
	void set_auditory_encoder_ptr(Auditory_encoder_base * auditory_encoder_ptr_);
	Auditory_encoder_base * get_auditory_encoder_ptr() const
		{return auditory_encoder_ptr;}

	void set_parameter(const Parameter_specification& param_spec);
	void describe_parameters(Output_tee& ot) const;
	
	/* direct inputs - 
	   object name is supplied along with all relevant information - no backwards lookup necessary
	   returns true if a change was made to data base (and so input should be processed further) and false otherwise.
	   Some functions return the previous value, and do nothing unless it is different from the new value.
	*/
	// stream inputs
	virtual void create_stream(const Symbol& name, double pitch_, double loudness_, GU::Point location);
	virtual void destroy_stream(const Symbol&);
//	virtual void erase_stream(const Symbol&);
	virtual GU::Point set_stream_location(const Symbol&, GU::Point);
	virtual double set_stream_pitch(const Symbol& stream_name, double pitch);
	virtual double set_stream_loudness(const Symbol& stream_name, double loudness);
	virtual GU::Size set_stream_size(const Symbol&, GU::Size);
	virtual Symbol set_stream_property(const Symbol&, const Symbol&, const Symbol&);

	// sound inputs
	virtual void make_new_sound_start(const Symbol& sound_name, const Symbol& stream_name, long time_stamp,
		GU::Point location, const Symbol& timbre, double loudness, long intrinsic_duration);
//	virtual void make_new_speech_start(const Symbol& sound_name, const Symbol& stream_name, long time_stamp, 
//		const Symbol& content, const Symbol& speaker_gender, const Symbol& speaker_id, double loudness, long duration);
	virtual void make_new_speech_start(const Speech_word& word);
	virtual void make_sound_stop(const Symbol&);
//	virtual void make_sound_event(const Symbol&, const Symbol&, const Symbol&, 
//		long, long intrinsic_duration = 0);
//	virtual void make_speech_sound_event(const Symbol&, const Symbol&, const Symbol&, long);
//	virtual void erase_sound(const Symbol&);
	virtual Symbol set_sound_property(const Symbol&, const Symbol&, const Symbol&);

	// event interface
//	virtual void accept_event(const Start_event *);
	virtual void accept_event(const Auditory_event *);
	virtual void handle_event(const Auditory_Delay_event *);
	virtual void accept_event(const Stop_event *);
	
	// allow Auditory_encoder_base to have access
	friend class Auditory_encoder_base;


private:
	// state

	// parameters
	Parameter appearance_delay;
	Parameter disappearance_delay;
	Parameter location_delay;
	Parameter recoded_location_delay;
//	Parameter property_time_fluctuation;
	Parameter recoding_time_fluctuation;
	Parameter transient_decay_time;
	Parameter recoding_failure_rate1;
	// recoding maps = how do they work?
	typedef std::map<Symbol, long> Recoding_times_t;
	Recoding_times_t recoding_times;
	typedef std::map<Symbol, Symbol> Category_recodings_t;
	Category_recodings_t category_recodings;
	
	// helper functions
	void setup();
	Smart_Pointer<Auditory_sound> get_sensory_object_ptr(const Symbol& object_name);
	void initialize_recodings();
	
	// pointer to custom encoder object
	Auditory_encoder_base * auditory_encoder_ptr;	// set externally with address supplied by a dynamic library

	
	// no default copy, assignment
	Auditory_perceptual_processor(const Auditory_perceptual_processor&);
	Auditory_perceptual_processor& operator= (const Auditory_perceptual_processor&);
};

#endif
