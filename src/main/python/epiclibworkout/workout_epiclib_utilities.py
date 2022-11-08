from epiclibworkout.epiclibgym import *
import pandas as pd

print(f"{LIBNAME=}")
cppyy.load_library(LIBNAME)

epiclib_include("Model-View Classes/View_base.h")
epiclib_include("Model-View Classes/Model.h")
epiclib_include("Framework classes/Output_tee_globals.h")
epiclib_include("Framework classes/Device_base.h")
epiclib_include("Framework classes/Device_exception.h")
epiclib_include("Framework classes/Device_processor.h")
epiclib_include("Framework classes/Human_base.h")
epiclib_include("Framework classes/Human_processor.h")
epiclib_include("Framework classes/Parameter.h")
epiclib_include("Framework classes/Coordinator.h")
epiclib_include("Framework classes/Processor.h")
epiclib_include("Utility Classes/Symbol.h")
epiclib_include("Utility Classes/Symbol_utilities.h")
epiclib_include("Utility Classes/Output_tee.h")
epiclib_include("Utility Classes/Geometry.h")
epiclib_include("Utility Classes/Statistics.h")
epiclib_include("Utility Classes/Point.h")
epiclib_include("Utility Classes/Symbol_Geometry_utilities.h")
epiclib_include("Utility Classes/Random_utilities.h")

epiclib_include("Standard_Symbols.h")
epiclib_include("PPS/PPS Interface classes/PPS_globals.h")
epiclib_include("Framework classes/Device_event_types.h")
epiclib_include("Motor Classes/Manual_actions.h")
epiclib_include("Motor Classes/Manual_processor.h")

from cppyy.gbl import Model
from cppyy.gbl import Coordinator
from cppyy.gbl import Normal_out
from cppyy.gbl import Geometry_Utilities as GU
from cppyy.gbl import Mean_accumulator
from cppyy.gbl import set_random_number_generator_seed
from cppyy.gbl import Symbol, concatenate_to_Symbol

def do_routine():

    data = list()

    DEBUG = True

    # @@@@@@@@@@@@ Geometry.h @@@@@@@@@@@@@@@@@@

    o = GU
    data.extend(exercise_namespace(o, ns_name='GU', print_result=DEBUG))

    o = GU.Point()
    data.extend(exercise_object(o, obj_name='GU.Point', namespace='GU', print_result=DEBUG))

    o = GU.Line_segment()
    data.extend(exercise_object(o, obj_name='GU.Line_segment', namespace='GU', print_result=DEBUG))

    o = GU.Polar_vector()
    data.extend(exercise_object(o, obj_name='GU.Polar_vector', namespace='GU', print_result=DEBUG))

    o = GU.Cartesian_vector()
    data.extend(exercise_object(o, obj_name='GU.Cartesian_vector', namespace='GU', print_result=DEBUG))

    o = GU.Polygon()
    data.extend(exercise_object(o, obj_name='GU.Polygon', namespace='GU', print_result=DEBUG))

    # @@@@@@@@@@@@ Symbol.h @@@@@@@@@@@@@@@@@@

    o = Symbol()
    data.extend(exercise_object(o, obj_name='Symbol', namespace='', print_result=DEBUG))

    # FIXME: I don't know how to test add-on methods like in Symbol_Geometry_utilities
    #        or random functions that are not methods of a class or struct
    # o = Symbol()
    # data.extend(exercise_namespace(o, ns_name='Symbol_Geometry_utilities', print_result=DEBUG))

    # CREATE DataFrame AND SAVE

    # CLEANUP =>\n that you get when results are exceptions
    out_data = []
    for data_dict in data:
        out_data.append({k: clean_result(v) if k == 'result' else v for k, v in data_dict.items()})

    # SAVE the data
    df = pd.DataFrame(out_data)
    df.to_csv('../../../code_exercise_results.csv', sep='\t', index=False)

    sys.exit()
