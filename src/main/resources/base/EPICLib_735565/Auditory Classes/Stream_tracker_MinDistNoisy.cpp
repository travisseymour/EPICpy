//
//  Stream_tracker_MinDist.cpp
//  EPICXAF
//
//  Created by David Kieras on 1/16/13.
//
//

#include "Stream_tracker_MinDistNoisy.h"
#include "Stream_base.h"
#include "Stream_type_factory.h"
#include "../Utility Classes/Symbol_utilities.h"
#include "../Standard_Symbols.h"
#include "../Utility Classes/Numeric_utilities.h"
#include "../Utility Classes/Random_utilities.h"
#include "../Utility Classes/Assert_throw.h"
#include "../Framework classes/Output_tee_globals.h"
#include <limits>
#include <algorithm>

using std::vector;
using std::endl;
using std::random_shuffle;
using std::next_permutation;

const Symbol Stream_assignment_c("Stream_assignment");

Stream_tracker_MinDistNoisy::Stream_tracker_MinDistNoisy(const std::string& stream_type_name_)
    : Stream_tracker_base(stream_type_name_), lambda(0.75), theta(0.35), alpha(0.05)
{
}

void Stream_tracker_MinDistNoisy::set_lambda(double lambda_)
{
	lambda = lambda_;
}
void Stream_tracker_MinDistNoisy::set_theta(double theta_)
{
	theta = theta_;
}

void Stream_tracker_MinDistNoisy::set_alpha(double alpha_)
{
	alpha = alpha_;
}



// call for each word set after the first, to assign the words to the streams
void Stream_tracker_MinDistNoisy::assign_sounds_to_streams()
{
    // We need to assign each word to one stream so that each stream has one word.
    // Veridical stream_ID in word is ignored
    
    // this work does not require distingishing "this_sound" from the other sounds
    // randomize them so that the assignment won't default to "good" case if attributes are tied
    std::random_shuffle(sounds.begin(), sounds.end());
    // calculate simple distance of each sound to each stream in a 2-d array
//    const int max_n_sounds_present = 4;
    // we will find the minimum total distance assignment of sounds to streams by
    // generating all permutations of sound-to-stream assignment,
    // and which one produces the minimum total.
    
    // the subscript of this vector represents the stream index;
    // the values in a cell represent the sound assigned to that stream.
    // start with the cells containing the sound indicies in sorted order.
    Assert(sounds.size() == streams.size());
    vector<int> assignments;
    for(int sound_index = 0; sound_index < sounds.size(); sound_index++)
        assignments.push_back(sound_index);
    Assert(assignments.size() == streams.size());
    // get the total distance of the starting arrangement, and save that arrangement
    double min_total_dist = get_total_distance(assignments);
    // we will be tracking the maximum distance found as well
    double max_total_dist = get_total_distance(assignments);
    vector<int> min_total_distance_assignment(assignments);
    // this loop continues until the next_permutation is the same as the starting in-order assignment
    while(next_permutation(assignments.begin(), assignments.end())) {
        double total_dist = get_total_distance(assignments);
        if(total_dist > max_total_dist) {
            max_total_dist = total_dist;
            }
        if(total_dist < min_total_dist) {
            min_total_dist = total_dist;
            min_total_distance_assignment = assignments;
            }
        }
    // at this point, min_total_dist and min_total_distance_assignments should have the final minimum values
    // and max_total_dist will have the maximum value obtained in the assignments
    // does the difference between max_total_dist and min_total_dist exceed the threshold?
    // if not, then pick from a random shuffle of the assignment
    Assert(max_total_dist >= min_total_dist);
    if((max_total_dist - min_total_dist) <= theta) {
		// for two streams, interchange the two cells
//		Assert(min_total_distance_assignment.size() == 2);
//		int temp = min_total_distance_assignment[0];
//		min_total_distance_assignment[0] = min_total_distance_assignment[1];
//		min_total_distance_assignment[1] = temp;
        // below is supposed to be correct 052114
        random_shuffle(min_total_distance_assignment.begin(), min_total_distance_assignment.end());
        // save the best assignment 
 //       assignments = min_total_distance_assignment;
        // randomly shuffle the assignment until a different value is obtained
 //      do {
//           random_shuffle(min_total_distance_assignment.begin(), min_total_distance_assignment.end());
//           } while (assignments == min_total_distance_assignment);
        }
    else if(biased_coin_flip(alpha)) {
// 		Assert(min_total_distance_assignment.size() == 2);
//		int temp = min_total_distance_assignment[0];
//		min_total_distance_assignment[0] = min_total_distance_assignment[1];
//		min_total_distance_assignment[1] = temp;
//      random_shuffle(min_total_distance_assignment.begin(), min_total_distance_assignment.end());
        // below was supposed to be correct 052114
        // randomly shuffle the assignment until a different value is obtained
        // save the best assignment
        assignments = min_total_distance_assignment;
        do {
            random_shuffle(min_total_distance_assignment.begin(), min_total_distance_assignment.end());
           } while (assignments == min_total_distance_assignment);
        }

    // go through the final assignment and assign the sounds to the corresponding streams
    for(int stream_index = 0; stream_index < min_total_distance_assignment.size(); stream_index++) {
        int sound_index = min_total_distance_assignment[stream_index];
        sounds[sound_index]->set_property(Stream_assignment_c, streams[stream_index]->get_name());
        streams[stream_index]->update(sounds[sound_index]->get_pitch(), sounds[sound_index]->get_loudness());
//        Normal_out << "sound " << sound_index << " assigned to stream " << stream_index << endl;
        }
/*

    double distances[max_n_sounds_present][max_n_sounds_present]; // first index is sound index, second is stream index
    // n_sounds_present should also be the number of streams present
    Assert(sounds.size() == streams.size());
    for(int sound_index = 0; sound_index < sounds.size(); sound_index++)
        for(int stream_index = 0; stream_index < sounds.size(); stream_index++) {
            double distance = get_distance(
                sounds[sound_index]->get_pitch(), sounds[sound_index]->get_loudness(),
                streams[stream_index]);
            distances[sound_index][stream_index] = distance;
        }
    // array has the distance for each sound/stream pair.  Pick the assignment that has the minimum total distance.
    // This version only works for two stream case.
    Assert(sounds.size() == 2);
    double dist11 = distances[0][0] + distances[1][1]; // strm1, sound1; strm2, sound2
    double dist12 = distances[0][1] + distances[1][0]; // strm1, sound2; strm2, sound1
    if(dist11 <= dist12) {
        sounds[0]->set_property(Stream_assignment_c, streams[0]->get_name());
        streams[0]->update(sounds[0]->get_pitch(), sounds[0]->get_loudness());
        sounds[1]->set_property(Stream_assignment_c, streams[1]->get_name());
        streams[1]->update(sounds[1]->get_pitch(), sounds[1]->get_loudness());
        }
    else {
        sounds[0]->set_property(Stream_assignment_c, streams[1]->get_name());
        streams[1]->update(sounds[0]->get_pitch(), sounds[0]->get_loudness());
        sounds[1]->set_property(Stream_assignment_c, streams[0]->get_name());
        streams[0]->update(sounds[1]->get_pitch(), sounds[1]->get_loudness());
        }
*/
}

// the subscript of this vector represents the stream index;
// the values in a cell represent the sound assigned to that stream.
double Stream_tracker_MinDistNoisy::get_total_distance(vector<int> assignments) const
{
    double total = 0;
    for(int stream_index = 0; stream_index < assignments.size(); stream_index++) {
        int sound_index = assignments[stream_index];
        total += get_distance(
                sounds[sound_index]->get_pitch(), sounds[sound_index]->get_loudness(),
                streams[stream_index]);
        }
    return total;
}


// get distance of supplied sound from specified stream
double Stream_tracker_MinDistNoisy::get_distance(double pitch, double loudness, std::shared_ptr<Stream_base> stream) const
{
//	return get_distance(pitch, loudness, stream.get_pitch_mean(), stream.get_loudness_mean());
	return get_distance(pitch, loudness, stream->get_predicted_pitch(), stream->get_predicted_loudness());
}


// simple calculation of distance between two sounds
double Stream_tracker_MinDistNoisy::get_distance(double pitch1, double loudness1, double pitch2, double loudness2) const
{
	double pitch_diff = fabs(pitch1 - pitch2); // difference in semitones
    pitch_diff = (pitch_diff > 4) ? 4. : pitch_diff;	// cap at 4
	double loudness_diff = loudness1 - loudness2;

//	const double lambda = 0.95;
	pitch_diff = pitch_diff * lambda;
	loudness_diff = loudness_diff * (1.0 - lambda);
	
	double sum = (pitch_diff * pitch_diff + loudness_diff * loudness_diff);
	return (sum > 0.0) ? sqrt(sum) : 0.0;  // avoid computing nan from a sqrt
}


