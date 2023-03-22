//
//  Stream_base.cpp
//  EPICXAF
//
//  Created by David Kieras on 1/16/13.
//
//

#include "Stream_base.h"

void Stream_base::reset()
{
    disappearance_time = 0;
    do_reset();
}

void Stream_base::update(double pitch, double loudness)
{
	disappearance_time = 0;
    do_update(pitch, loudness);
}


