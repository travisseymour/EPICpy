import re
import sys
from functools import partial
from typing import Optional

from cppinclude import epiclib_include
import cppyy
from loguru import logger as log
from pprint import pprint
from apputils import LIBNAME
import random
from io import StringIO  ## for Python 3

# ------------------------------------------------------
# Load Various Include files and objects we will need
# The location of the library depends on OS, this is
# figured out in main.py which sets apputils.LIBNAME
# so that the correct library can be loaded when this
# module is imported.
# ------------------------------------------------------

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
epiclib_include("Utility Classes/Output_tee.h")
epiclib_include("Utility Classes/Geometry.h")
epiclib_include("Utility Classes/Statistics.h")
epiclib_include("Utility Classes/Point.h")
epiclib_include("Standard_Symbols.h")
epiclib_include("PPS/PPS Interface classes/PPS_globals.h")
epiclib_include("Framework classes/Device_event_types.h")
epiclib_include("Motor Classes/Manual_actions.h")
epiclib_include("Motor Classes/Manual_processor.h")

from cppyy.gbl import Model
from cppyy.gbl import Coordinator
from cppyy.gbl import Normal_out
from cppyy.gbl import Geometry_Utilities as GU



def random_point(maximum: float = 100.00) -> GU.Point:
    return GU.Point(
        random.uniform(0.0, maximum),
        random.uniform(0.0, maximum)
    )


def random_size(maximum: float = 100.00) -> GU.Point:
    return GU.Size(
        random.uniform(0.0, maximum),
        random.uniform(0.0, maximum)
    )


def random_line_segment(maximum: float = 100.00) -> GU.Line_segment:
    p1 = random_point()
    p2 = GU.Point(p1.x + random.uniform(0.0, maximum), p1.y + random.uniform(0.0, maximum))
    return GU.Line_segment(p1, p2)

def random_polar_vector(kind: str)->GU.Polar_vector:
    if kind == 'double,double':
        return GU.Polar_vector(random.uniform(0.0,100.00), random.uniform(0.0,100.00))
    elif kind == 'point,point':
        return GU.Polar_vector(random_point(), random_point())
    elif kind == 'Cartesian_vector':
        return GU.Polar_vector(random_cartesian_vector('double,double'))
    else:
        raise NotImplementedError(f'no random pv for {kind=}')

def random_cartesian_vector(kind: str)->GU.Cartesian_vector:
    if kind == 'double,double':
        return GU.Cartesian_vector(random.uniform(0.0, 100.0), random.uniform(0.0, 100.0))
    elif kind == 'point,point':
        return GU.Cartesian_vector(random_point(), random_point())
    elif kind == 'Polar_vector':
        return GU.Cartesian_vector(random_polar_vector('double,double'))
    else:
        raise NotImplementedError(f'no random cv for {kind=}')

def test_geometry():
    random.seed(1138)
    data = list()



    '''
    staticmethods
    '''
    data.append(
        ['to_radians()'] +
        [GU.to_radians(theta_d) for theta_d in [random.uniform(0.0, 100.00) for _ in range(10)]]
    )
    data.append(
        ['to_degrees()'] +
        [GU.to_radians(theta_d) for theta_d in [random.uniform(0.0, 100.00) for _ in range(10)]]
    )
    data.append(
        ['degrees_subtended()'] +
        [GU.degrees_subtended(size_measure, distance_measure) for size_measure, distance_measure in
         [(random.uniform(0.0, 100.00), random.uniform(0.0, 100.00)) for _ in range(10)]]
    )
    data.append(
        ['units_per_degree_subtended()'] +
        [GU.units_per_degree_subtended(size_measure, distance_measure) for size_measure, distance_measure in
         [(random.uniform(0.0, 100.00), random.uniform(0.0, 100.00)) for _ in range(10)]]
    )
    data.append(
        ['cartesian_distance()'] +
        [GU.cartesian_distance(p1, p2) for p1, p2 in [(random_point(), random_point()) for _ in range(10)]]
    )

    data.append(
        ['is_point_inside_rectangle()'] +
        [GU.is_point_inside_rectangle(random_point(), random_point(), random_size()) for _ in
         [random.random() for _ in range(10)]]
    )

    data.append(
        ['clip_line_to_rectangle()'] +
        [str(GU.clip_line_to_rectangle(random_line_segment(), random_point(), random_size())) for _ in
         [random.random() for _ in range(10)]]
    )

    # SKIPPING: compute_center_intersecting_line

    data.append(
        ['closest_distance()'] +
        [GU.closest_distance(random_point(), random_point(), random_size()) for _ in
         [random.random() for _ in range(10)]]
    )


    '''
    testing equalities
    '''

    data.append(
        ['Point Equalities a a'] +
        [(a == a, a < a, a > a, a != a, a <= a, a >= a) for a in [random_point(10) for _ in range(10)]]
    )

    data.append(
        ['Point Equalities a b'] +
        [(a == b, a < b, a > b, a != b, a <= b, a >= b) for a, b in
         [(random_point(10), random_point(10)) for _ in range(10)]]
    )

    data.append(
        ['Size Equalities a'] +
        [(a == a, a != a) for a in [random_size(10) for _ in range(10)]]

    )

    data.append(
        ['Size Equalities a b'] +
        [(a == b, a != b) for a, b in [(random_size(10), random_size(10)) for _ in range(10)]]
    )


    '''
    testing class initializers
    '''

    data.append(
        ['Cartesian_vector(dbl,dbl)'] +
        [(cv.delta_x, cv.delta_y) for cv in [random_cartesian_vector('double,double') for _ in range(10)]]
    )

    data.append(
        ['Cartesian_vector(point,point)'] +
        [(cv.delta_x, cv.delta_y) for cv in [random_cartesian_vector('point,point') for _ in range(10)]]
    )

    data.append(
        ['Cartesian_vector(point,point)'] +
        [(cv.delta_x, cv.delta_y) for cv in [random_cartesian_vector('Polar_vector') for _ in range(10)]]
    )

    data.append(
        ['Polar_vector(dbl,dbl)'] +
        [(cv.r, cv.theta) for cv in [random_polar_vector('double,double') for _ in range(10)]]
    )

    data.append(
        ['Polar_vector(point,point)'] +
        [(cv.r, cv.theta) for cv in [random_polar_vector('point,point') for _ in range(10)]]
    )

    data.append(
        ['Polar_vector(point,point)'] +
        [(cv.r, cv.theta) for cv in [random_polar_vector('Cartesian_vector') for _ in range(10)]]
    )

    data.append(
        ['Size(double,double)'] +
        [(sz.h, sz.v) for sz in [random_size() for _ in range(10)]]
    )

    '''
    testing class methods
    '''

    data.append(
        ['Line_segment()'] +
        [(str(ls.get_p1()), str(ls.get_p2()), str(ls.get_dx()), str(ls.get_dy()), str(ls.get_center()), str(ls.get_size()), str(ls.get_A()), str(ls.get_B()), str(ls.get_C()), ls.is_horizontal(), ls.is_vertical(), ls.is_on_infinite_lint(random_point()), ls.closest_point_on_infinite_line(random_point()), ls.distance_from_infinite_line(random_point())) for ls in [random_line_segment() for _ in range(10)]]
    )












    '''
    print it for now
    '''

    for datum in data:
        print(datum)

def get_help_text(obj)->str:
    io = StringIO('')
    sys.stdout = io
    help(obj)
    sys.stdout = sys.__stdout__
    return io.getvalue().replace(' |  ', '')

def get_methods_text(help_text:str)->str:
    txt = help_text.replace('Methods defined here:', '-' * 70)
    sections = txt.split('-' * 70)
    return sections[1].strip()

def get_weakref_properties(help_text:str)->list:
    top = 'Data descriptors defined here:'
    if top not in help_text:
        return []
    txt = help_text[help_text.find(top):]
    if not txt:
        return []
    txt = txt.replace(top, '')
    sections = txt.split('-' * 70)
    sections = [section for section in sections if '__weakref__' in section]
    if not sections:
        return []
    section = sections[0][sections[0].find('__weakref__'):].replace('__weakref__', '')
    lines = section.splitlines(keepends=False)
    properties = [aline.strip() for aline in lines if aline and not aline.startswith(' ')]
    return properties

def get_methods(methods_text:str)->list:
    # split by section so we can remove __assign__(...) and __init__(...) sections
    methods  = [method for method in methods_text.strip().split('\n\n') if not method.startswith('__')]
    # put back together for line by line processing
    methods = '\n\n'.join(methods).splitlines(keepends=False)
    # remove stubs
    methods = [aline.removeprefix('    ') for aline in methods if aline.startswith('    ') and not aline.endswith('.')]
    # clean
    methods = [cleanup(method) for method in methods]
    return methods


def get_initializers(methods_text:str)->list:
    # split by section so we can only accept __init__(...) section
    methods  = [method for method in methods_text.strip().split('\n\n') if method.startswith('__init__')]
    # put back together for line by line processing
    methods = '\n\n'.join(methods).splitlines(keepends=False)
    # remove stubs
    methods = [aline.removeprefix('    ') for aline in methods if aline.startswith('    ')]
    # clean
    methods = [cleanup(method) for method in methods]
    return methods

def get_properties(methods_text:str)->list:
    '''AFAIK, these properties only show up in structs (like Point). Otherwise DK uses get_xxx() methods'''
    # split by section so we can only accept __weakref__(...) section
    methods  = [method for method in methods_text.strip().split('\n\n') if method.startswith('__weakref__')]
    # put back together for line by line processing
    properties = '\n\n'.join(methods).splitlines(keepends=False)
    # clean
    properties = [prop.strip() for prop in properties]
    return properties

def cleanup(text:str)->str:
    # removals
    txt = re.sub(r'(&| *const *| *extern *)', '', text).replace('  ', ' ')
    # replacements
    txt = txt.replace('Geometry_Utilities', 'GU')
    txt = re.sub(r"\w+::", '', txt)
    return txt

def get_func_sig(method_text:str)->Optional[tuple]:
    try:
        func, params = re.search(r'([^\(]+)\(([^\)]*)\)', method_text).groups()
        func = func.split(' ')[-1]
        func = func.strip()
        params = params.strip()
        if params:
            # We just want the types
            params = [param.split(' ')[0].strip() for param in re.split(r' *, *', params)]

        # print(f'{func=}')
        # print(f'{params=}')

        return func, params

    except Exception as e:
        log.exception(e)
        return None

def get_calls(func_sigs:list, type_makers: dict)->list:
    calls = list()
    for method in func_sigs:
        func, params = get_func_sig(method)
        if not params:
            func_sig = f"{func}()"
        else:
            rparams = [type_makers[param] for param in params]
            rparams = ', '.join(rparams)
            func_sig = f"{func}({rparams})"
        calls.append(func_sig)
    return calls

def test_namespace(namespace)->list:
    '''
    Like test_object but where you are just exercise staticmethods in a namespace
    '''
    ...

def test_object(obj, init_properties:Optional[list]=None)->list:
    '''
    Given an object, exercise its initializers and methods.
    Note that these are not tests because there is no target.
    We're just asking what a set of code does across a range of inputs
    (currently the idea is to use this infor to test the python version
    of EPICLib against DK's C++ version)

    NOTE: Some objects (e.g., Point) have attributes like .x and .y
    that can be used to make sure initializers are working as expected.
    You can specify the ones you want used as init_properties, e.g.:
    ['x', 'y']
    '''

    makers = {
        'long': partial(random.randint,a=0,b=100),
        'double': 'random.uniform()',
        'Point': 'random_point()',
        'Line_segment': 'random_line_segment()',
        'Polar_vector': 'random_polar_vector()',
        'Size': 'random_size()',
        'Cartesian_vector': 'random_cartesian_vector()'
    }

    # get all available info about the object
    obj_help_text = get_help_text(obj)
    methods_text = get_methods_text(obj_help_text)
    the_inits = get_initializers(methods_text)
    the_methods = get_methods(methods_text)
    the_properties = get_properties(methods_text)
    the_properties = get_weakref_properties(obj_help_text)
    the_properties = the_properties if the_properties else None

    # get python calls we can make with eval/exec to exercise initializers and methods
    init_calls = get_calls(the_inits, makers) if the_inits else None
    method_calls = get_calls(the_methods, makers) if the_methods else None

    print('*** INIT CALLS ***')
    pprint(init_calls, width=100)
    print('\n\n*** METHOD CALLS ***')
    pprint(method_calls, width=100)
    print('\n\n*** OBJECT PROPERTIES ***')
    pprint(the_properties, width=100)


def run_tests():
    p = GU.Point()
    test_object(p)
    print('\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n')
    ls = GU.Line_segment()
    test_object(ls)

    sys.exit()