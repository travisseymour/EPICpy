/*
The Ocular_processor and Invol_ocular_processor interact with each other at execution.

The Ocular_processor handles voluntary eye movement execution as follows:
If an involuntary movement is underway, then execution of a voluntary movement
is deferred until the involuntary one is complete, whereupon the voluntary movement
is started. 

The Invol_ocular_processor handles involuntary eye movement execution as follows:
If a voluntary movement is underway, then the prepared involuntary movement is simply
discarded. 
When an involuntary movement completes, if a prepared voluntary movement is waiting,
then the Ocular_processor starts executing it.

This interaction is handled by overriding the "Template method" functions in Motor_processor
for execute_action() and complete_action().

*/


#ifndef OCULAR_PROCESSOR_H
#define OCULAR_PROCESSOR_H

#include "Motor_processor.h"
#include "../Framework classes/Parameter.h"

class Ocular_action;

class Ocular_processor : public Motor_processor {
public:
	Ocular_processor(Human_processor * human_ptr) :
		Motor_processor("Ocular", human_ptr),
		saccade_intercept("Voluntary_saccade_intercept", 21),	// values from Carpenter(1988)
		saccade_slope("Voluntary_saccade_slope", 2.2)
		{setup();}
	
	virtual void initialize();

//	services for Ocular_actions
	friend class Ocular_action;
	
protected:
	// override to allow deferral of initiation
	virtual void execute_action();

private:
	// parameters
	Parameter saccade_intercept;
	Parameter saccade_slope;
	
	// helper functions
	void setup();
	
	// no default copy, assignment
	Ocular_processor(const Ocular_processor&);
	Ocular_processor& operator= (const Ocular_processor&);
};



#endif
