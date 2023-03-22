//
// Created by nogard on 10/10/20.
//

#include "Epic_py_utils.h"


#include "PPS/PPS Interface classes/PPS_globals.h"
#include "Framework classes/Output_tee_globals.h"

void Normal_out_write(std::string text) {
    Normal_out << text;
}

void Trace_out_write(std::string text) {
    Trace_out << text;
}

void PPS_out_write(std::string text) {
    PPS_out << text;
}