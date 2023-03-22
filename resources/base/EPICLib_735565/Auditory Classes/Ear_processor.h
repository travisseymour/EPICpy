#ifndef EAR_PROCESSOR_H
#define EAR_PROCESSOR_H

//#include <map>

//#include "Output_tee.h"
#include "../Framework classes/Human_subprocessor.h"
#include "Auditory_store_processor.h"
#include "../Utility Classes/Geometry.h"
namespace GU = Geometry_Utilities;
#include "../Framework classes/Parameter.h"
#include "Auditory_physical_store.h"
#include "Auditory_event_types.h"
#include "../Utility Classes/Statistics.h"
#include <map>

class Human_processor;
class Symbol;
struct Speech_word;
class Stream_tracker_base;

/* The Ear_processor accepts direct inputs from Auditory_physical_store, and emits events
to Auditory_sensory_store after the appropriate delays. It stores no information of its own.
*/

class Ear_processor : public Auditory_processor {
public:
	Ear_processor(Human_processor * human_ptr_) :
		Auditory_processor ("Ear", human_ptr_), 
		// delay for new streams and sounds to be passed on
		appearance_window("Appearance_window_time", 10),
//		appearance_delay("Appearance_transduction_time", 25),
		appearance_delay("Appearance_transduction_time", 10),
		disappearance_window("Disappearance_window_time", 10),
		// delay for cessation of streams and sounds to be passed on
		// this stretches out the effective duration of a stream or sound
		disappearance_delay("Disappearance_transduction_time", 100),
		// delay for passing on a change in stream location or size
		location_delay("Location_change_transduction_time", 10),
		// delay for passing on a change in a property
		property_window("Property_window_time", 15),
		property_delay("Property_transduction_time", 100),
// modified From Greg 060714 xxxJun02RepAll_UWYH_Trk43ab_Fitv23ab
		effective_snr_pitch_weight("Effective_snr_pitch_weight", 3.0),
		pitch_difference_max("Pitch_difference_cap", 4.0),
		content_detection1_dist_mean("Content_detection1_dist_mean", -15.0),
		content_detection2_dist_mean("Content_detection2_dist_mean", -17.0),
		content_detection3_dist_mean("Content_detection3_dist_mean", -24.0),
		content_detection_dist_sd("Content_detection_dist_sd", 10.0),
		stream_alpha("Stream_alpha", 0.02),
		stream_lambda("Stream_lambda", 0.65),
		stream_theta("Stream_theta", 0.55),
		stream_tracker_ptr(nullptr)
		{setup();}
	~Ear_processor();

	virtual void initialize();
	
	/* direct inputs - 
	   object name is supplied along with all relevant information - no backwards lookup necessary
	   returns true if a change was made to data base (and so input should be processed further) and false otherwise.
	   Some functions return the previous value, and do nothing unless it is different from the new value.
	*/
	// stream inputs
//	virtual void create_stream(const Symbol& stream_name, GU::Point location, GU::Size size = GU::Size());
	virtual void create_stream(const Symbol& stream_name, double pitch, double loudness, GU::Point location);
	virtual void destroy_stream(const Symbol& stream_name);
//	virtual void erase_stream(const Symbol& stream_name);
	virtual GU::Point set_stream_location(const Symbol& stream_name, GU::Point location);
	virtual double set_stream_pitch(const Symbol& stream_name, double pitch);
	virtual double set_stream_loudness(const Symbol& stream_name, double loudness);
	virtual GU::Size set_stream_size(const Symbol& stream_name, GU::Size size);
	virtual Symbol set_stream_property(const Symbol& stream_name, const Symbol& propname, const Symbol& propvalue);

	// sound inputs
	virtual void make_new_sound_start(const Symbol& sound_name, const Symbol& stream_name, long time_stamp, GU::Point location, const Symbol& timbre, double loudness, long intrinsic_duration);
//	virtual void make_new_speech_start(const Symbol& sound_name, const Symbol& stream_name, long time_stamp, 
//		const Symbol& content, const Symbol& speaker_gender, const Symbol& speaker_id, double loudness, long duration);
	virtual void make_new_speech_start(const Speech_word& word);
	virtual void make_sound_stop(const Symbol& sound_name);	
//	virtual void make_sound_event(const Symbol& sound_name, const Symbol& stream_name, const Symbol& timbre, double loudness, long duration, long intrinsic_duration = 0);
//	virtual void make_speech_sound_event(const Symbol& sound_name, const Symbol& stream_name, const Symbol& utterance, double loudness, long duration);
//	virtual void erase_sound(const Symbol& sound_name);
	virtual Symbol set_sound_property(const Symbol& sound_name, const Symbol& propname, const Symbol& propvalue);


	// event interface
//	virtual void accept_event(const Start_event *);
	virtual void accept_event(const Stop_event *);
	virtual void accept_event(const Auditory_event *);
	
	// event interface to produce processing window
	virtual void handle_event(const Auditory_Stream_Destroy_event *);
	virtual void handle_event(const Auditory_Sound_Start_event *);
	virtual void handle_event(const Auditory_Speech_Start_event *);
	virtual void handle_event(const Auditory_Sound_Stop_event *);
	virtual void handle_event(const Auditory_Sound_Set_Property_event * event_ptr);
		
	// services
			

private:

	// state

	// parameters
	Parameter appearance_window;
	Parameter appearance_delay;
	Parameter disappearance_window;
	Parameter disappearance_delay;
	Parameter location_delay;
	Parameter property_window;
	Parameter property_delay;
	Parameter effective_snr_pitch_weight;
	Parameter pitch_difference_max;
	Parameter content_detection1_dist_mean;
	Parameter content_detection2_dist_mean;
	Parameter content_detection3_dist_mean;
	Parameter content_detection_dist_sd;
	Parameter stream_alpha;
	Parameter stream_lambda;
	Parameter stream_theta;
	
	// a pointer to the stream tracker in use
	Stream_tracker_base* stream_tracker_ptr;
		
	// helper functions
	void setup();
//	GU::Point location_noise(GU::Point location); // 09/09/13 superseded - dk
	// kludge to support model fitting:
	typedef std::map<Symbol, Symbol> Category_recodings_t;
	Category_recodings_t category_recodings;
	void initialize_recodings();

	
	virtual void make_new_sound_start_f(const Symbol& sound_name, const Symbol& stream_name, long time_stamp, GU::Point location,
		const Symbol& timbre, double loudness, long intrinsic_duration);
//	virtual void make_new_speech_start_f(const Symbol& sound_name, const Symbol& stream_name, long time_stamp, 
//		const Symbol& content, const Symbol& speaker_gender, const Symbol& speaker_id, double loudness, long duration);
	virtual void make_new_speech_start_f(const Speech_word& word);
	Symbol set_sound_property_f(const Symbol& sound_name, const Symbol& prop_name, const Symbol& prop_value);
	void make_sound_stop_f(const Symbol& sound_name);	
	
	Mean_accumulator pitch_stats;

	// no copy, assignment
	Ear_processor(const Ear_processor&);
	Ear_processor& operator= (const Ear_processor&);
};

#endif
