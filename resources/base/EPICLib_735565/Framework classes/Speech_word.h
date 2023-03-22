/*
 *  Speech_word.h
 *  EPICXAF
 *
 *  Created by David Kieras on 1/11/12.
 *  Copyright 2012 __MyCompanyName__. All rights reserved.
 *
 */

#ifndef SPEECH_WORD_H
#define SPEECH_WORD_H

#include "../Utility Classes/Symbol.h"
#include "../Utility Classes/Point.h"

// A package of speech word attributes to allow speech-handling
// functions to have a fixed signature even if attributes are
// added or removed.
struct Speech_word {
	Symbol name;		// unique name for each word object
	Symbol stream_name;	// verdical stream name
	long time_stamp;
	GU::Point location;
	double pitch;       // semitones
	double loudness;    // dB
	double duration;
	Symbol content;
	Symbol speaker_gender;
	Symbol speaker_id;
};





#endif
