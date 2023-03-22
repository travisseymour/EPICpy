//
//  Stream_tracker_MinDistNoisy.h
//  EPICXAF
//
//  Created by David Kieras on 2/11/13.
//
//

#ifndef STREAM_TRACKER_MINDISTNOISY_H
#define STREAM_TRACKER_MINDISTNOISY_H

#include "Stream_tracker_base.h"

class Stream_tracker_MinDistNoisy : public Stream_tracker_base {
public:
	Stream_tracker_MinDistNoisy(const std::string& stream_type_name_);
	void assign_sounds_to_streams() override;
	void set_lambda(double lambda_) override;
	void set_theta(double lambda_) override;
	void set_alpha(double lambda_) override;
    
private:
	double lambda; // pitch weight [0, 1]
	double theta;   // threshold for distance to be use rather than random assignment
	double alpha;   // probably of random assignment rather than distance
    double get_total_distance(std::vector<int> assignments) const;
    // calculating distances between sounds and stream values
	double get_distance(double pitch, double loudness, std::shared_ptr<Stream_base> stream) const;
	double get_distance(double pitch1, double loudness1, double pitch2, double loudness2) const;
};

#endif 
